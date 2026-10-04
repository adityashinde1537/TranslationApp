import hashlib
import importlib.util
import logging
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import snapshot_download
from pydantic import BaseModel, Field

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "hari31416/indictrans2-indic-indic-dist-320M-ONNX-int8",
)
MODEL_REVISION = os.getenv(
    "MODEL_REVISION",
    "b04956dee2f2a3e06e44bf09f8d654a6b81af99a",
)
SOURCE_LANGUAGE_CODE = "hin_Deva"
TARGET_LANGUAGE_CODE = "sat_Olck"
SOURCE_LANGUAGE_NAME = "Hindi"
TARGET_LANGUAGE_NAME = "Santhali (Ol Chiki)"
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "1500"))
MIN_OL_CHIKI_RATIO = float(os.getenv("MIN_OL_CHIKI_RATIO", "0.50"))

DEFAULT_CACHE_PATH = Path(__file__).resolve().parent / "translations.db"
CACHE_DB_PATH = Path(os.getenv("TRANSLATION_CACHE_DB", str(DEFAULT_CACHE_PATH)))

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("translation-backend")

app = FastAPI(
    title="Hindi to Santhali Translation API",
    version="2.0.0",
    description=(
        "IndicTrans2 INT8 ONNX-powered Hindi to Santhali "
        "(Ol Chiki) translation service."
    ),
)

cors_value = os.getenv("CORS_ORIGINS", "*")
cors_origins = ["*"] if cors_value == "*" else [
    origin.strip() for origin in cors_value.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_model: Any | None = None
_runtime_lock = threading.Lock()
_inference_lock = threading.Lock()


class TranslationRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_INPUT_CHARS,
        description="Hindi text written in Devanagari.",
    )


class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str = SOURCE_LANGUAGE_NAME
    target_language: str = TARGET_LANGUAGE_NAME
    latency_ms: int
    cached: bool


class HealthResponse(BaseModel):
    status: str
    model: str
    model_revision: str
    model_loaded: bool
    source_language_code: str
    target_language_code: str
    runtime: str


def init_cache() -> None:
    CACHE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(CACHE_DB_PATH, timeout=30) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS translations (
                cache_key TEXT PRIMARY KEY,
                source_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                model_name TEXT NOT NULL,
                source_language_code TEXT NOT NULL,
                target_language_code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def cache_key_for(text: str) -> str:
    value = "|".join(
        [
            MODEL_NAME,
            MODEL_REVISION,
            SOURCE_LANGUAGE_CODE,
            TARGET_LANGUAGE_CODE,
            text,
        ]
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def get_cached_translation(text: str) -> str | None:
    key = cache_key_for(text)
    try:
        with sqlite3.connect(CACHE_DB_PATH, timeout=30) as connection:
            row = connection.execute(
                "SELECT translated_text FROM translations WHERE cache_key = ?",
                (key,),
            ).fetchone()
        return row[0] if row else None
    except sqlite3.Error:
        logger.exception("Translation cache lookup failed")
        return None


def save_translation(text: str, translated_text: str) -> None:
    key = cache_key_for(text)
    try:
        with sqlite3.connect(CACHE_DB_PATH, timeout=30) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO translations (
                    cache_key,
                    source_text,
                    translated_text,
                    model_name,
                    source_language_code,
                    target_language_code
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    key,
                    text,
                    translated_text,
                    f"{MODEL_NAME}@{MODEL_REVISION}",
                    SOURCE_LANGUAGE_CODE,
                    TARGET_LANGUAGE_CODE,
                ),
            )
            connection.commit()
    except sqlite3.Error:
        logger.exception("Translation cache write failed")


def _load_runtime_from_snapshot(snapshot_path: str) -> Any:
    helper_path = Path(snapshot_path) / "translate.py"
    if not helper_path.exists():
        raise RuntimeError("IndicTrans2 ONNX helper was not found in the model snapshot.")

    spec = importlib.util.spec_from_file_location(
        "translationapp_indictrans_onnx",
        helper_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load IndicTrans2 ONNX helper module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    runtime_class = getattr(module, "IndicTransONNX", None)
    if runtime_class is None:
        raise RuntimeError("IndicTransONNX runtime class is unavailable.")

    return runtime_class(snapshot_path)


def get_runtime() -> Any:
    global _model

    if _model is not None:
        return _model

    with _runtime_lock:
        if _model is None:
            logger.info(
                "Downloading/loading translation model %s at revision %s",
                MODEL_NAME,
                MODEL_REVISION,
            )
            snapshot_path = snapshot_download(
                repo_id=MODEL_NAME,
                revision=MODEL_REVISION,
            )
            _model = _load_runtime_from_snapshot(snapshot_path)
            logger.info("IndicTrans2 ONNX translation model loaded")

    return _model


def ol_chiki_letter_ratio(text: str) -> float:
    alphabetic = [character for character in text if character.isalpha()]
    if not alphabetic:
        return 0.0

    ol_chiki_letters = sum(
        1
        for character in alphabetic
        if 0x1C5A <= ord(character) <= 0x1C7F
    )
    return ol_chiki_letters / len(alphabetic)


def has_meaningful_ol_chiki(text: str) -> bool:
    ol_chiki_letters = sum(
        1
        for character in text
        if 0x1C5A <= ord(character) <= 0x1C7F
    )
    return (
        ol_chiki_letters >= 2
        and ol_chiki_letter_ratio(text) >= MIN_OL_CHIKI_RATIO
    )


def translate_text(text: str) -> str:
    runtime = get_runtime()

    with _inference_lock:
        translated = runtime.translate(
            text,
            src_lang=SOURCE_LANGUAGE_CODE,
            tgt_lang=TARGET_LANGUAGE_CODE,
        )

    if not isinstance(translated, str):
        raise RuntimeError("Translation runtime returned an unexpected response.")

    translated = translated.strip()
    if not translated:
        raise RuntimeError("Translation runtime returned an empty response.")

    if not has_meaningful_ol_chiki(translated):
        raise RuntimeError(
            "Translation output did not contain enough Ol Chiki text."
        )

    return translated


init_cache()


@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model=MODEL_NAME,
        model_revision=MODEL_REVISION,
        model_loaded=_model is not None,
        source_language_code=SOURCE_LANGUAGE_CODE,
        target_language_code=TARGET_LANGUAGE_CODE,
        runtime="ONNX Runtime INT8 / CPU",
    )


@app.post("/translate", response_model=TranslationResponse)
def translate(request: TranslationRequest) -> TranslationResponse:
    started = time.perf_counter()
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=422, detail="Text cannot be blank.")

    cached = get_cached_translation(text)
    if cached is not None and has_meaningful_ol_chiki(cached):
        return TranslationResponse(
            translated_text=cached,
            latency_ms=round((time.perf_counter() - started) * 1000),
            cached=True,
        )

    try:
        translated = translate_text(text)
    except Exception as exc:
        logger.exception("Translation failed")
        raise HTTPException(
            status_code=503,
            detail="Hindi to Santhali translation is currently unavailable.",
        ) from exc

    save_translation(text, translated)

    return TranslationResponse(
        translated_text=translated,
        latency_ms=round((time.perf_counter() - started) * 1000),
        cached=False,
    )
