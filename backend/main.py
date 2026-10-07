import gc
import hashlib
import importlib.util
import logging
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import snapshot_download
from pydantic import BaseModel, Field

MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "1500"))

LANGUAGES = {
    "hi": {"name": "Hindi", "code": "hin_Deva"},
    "en": {"name": "English", "code": "eng_Latn"},
    "mr": {"name": "Marathi", "code": "mar_Deva"},
}

MODEL_SPECS = {
    "indic-indic": {
        "name": os.getenv(
            "INDIC_INDIC_MODEL_NAME",
            "hari31416/indictrans2-indic-indic-dist-320M-ONNX-int8",
        ),
        "revision": os.getenv(
            "INDIC_INDIC_MODEL_REVISION",
            "b04956dee2f2a3e06e44bf09f8d654a6b81af99a",
        ),
    },
    "en-indic": {
        "name": os.getenv(
            "EN_INDIC_MODEL_NAME",
            "hari31416/indictrans2-en-indic-dist-200M-ONNX-int8",
        ),
        "revision": os.getenv("EN_INDIC_MODEL_REVISION", "main"),
    },
    "indic-en": {
        "name": os.getenv(
            "INDIC_EN_MODEL_NAME",
            "hari31416/indictrans2-indic-en-dist-200M-ONNX-int8",
        ),
        "revision": os.getenv("INDIC_EN_MODEL_REVISION", "main"),
    },
}

DEFAULT_CACHE_PATH = Path(__file__).resolve().parent / "translations.db"
CACHE_DB_PATH = Path(os.getenv("TRANSLATION_CACHE_DB", str(DEFAULT_CACHE_PATH)))

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("translation-backend")

app = FastAPI(
    title="Hindi, English and Marathi Translation API",
    version="3.0.0",
    description=(
        "IndicTrans2 INT8 ONNX translation service for Hindi, English and Marathi."
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

_active_runtime: Any | None = None
_active_model_key: str | None = None
_runtime_lock = threading.Lock()
_inference_lock = threading.Lock()

LanguageCode = Literal["hi", "en", "mr"]


class TranslationRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_INPUT_CHARS,
        description="Text to translate.",
    )
    source_language: LanguageCode = "hi"
    target_language: LanguageCode = "en"


class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    latency_ms: int
    cached: bool


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    active_model: str | None
    supported_languages: dict[str, str]
    supported_directions: list[str]
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


def model_key_for(source_language: str, target_language: str) -> str:
    if source_language == "en":
        return "en-indic"
    if target_language == "en":
        return "indic-en"
    return "indic-indic"


def model_spec_for(source_language: str, target_language: str) -> dict[str, str]:
    return MODEL_SPECS[model_key_for(source_language, target_language)]


def cache_key_for(
    text: str,
    source_language: str,
    target_language: str,
) -> str:
    source_code = LANGUAGES[source_language]["code"]
    target_code = LANGUAGES[target_language]["code"]
    model_spec = model_spec_for(source_language, target_language)

    value = "|".join(
        [
            model_spec["name"],
            model_spec["revision"],
            source_code,
            target_code,
            text,
        ]
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def get_cached_translation(
    text: str,
    source_language: str,
    target_language: str,
) -> str | None:
    key = cache_key_for(text, source_language, target_language)
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


def save_translation(
    text: str,
    translated_text: str,
    source_language: str,
    target_language: str,
) -> None:
    key = cache_key_for(text, source_language, target_language)
    source_code = LANGUAGES[source_language]["code"]
    target_code = LANGUAGES[target_language]["code"]
    model_spec = model_spec_for(source_language, target_language)

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
                    f"{model_spec['name']}@{model_spec['revision']}",
                    source_code,
                    target_code,
                ),
            )
            connection.commit()
    except sqlite3.Error:
        logger.exception("Translation cache write failed")


def _load_runtime_from_snapshot(snapshot_path: str, model_key: str) -> Any:
    helper_path = Path(snapshot_path) / "translate.py"
    if not helper_path.exists():
        raise RuntimeError("IndicTrans2 ONNX helper was not found in the model snapshot.")

    module_name = f"translationapp_{model_key.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load IndicTrans2 ONNX helper module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    runtime_class = getattr(module, "IndicTransONNX", None)
    if runtime_class is None:
        raise RuntimeError("IndicTransONNX runtime class is unavailable.")

    return runtime_class(snapshot_path)


def get_runtime(model_key: str) -> Any:
    global _active_runtime, _active_model_key

    if _active_runtime is not None and _active_model_key == model_key:
        return _active_runtime

    with _runtime_lock:
        if _active_runtime is not None and _active_model_key == model_key:
            return _active_runtime

        model_spec = MODEL_SPECS[model_key]
        logger.info(
            "Downloading/loading translation model %s at revision %s",
            model_spec["name"],
            model_spec["revision"],
        )

        _active_runtime = None
        _active_model_key = None
        gc.collect()

        snapshot_path = snapshot_download(
            repo_id=model_spec["name"],
            revision=model_spec["revision"],
        )
        runtime = _load_runtime_from_snapshot(snapshot_path, model_key)

        _active_runtime = runtime
        _active_model_key = model_key
        logger.info("IndicTrans2 ONNX model loaded for %s", model_key)

    return _active_runtime


def translate_text(
    text: str,
    source_language: str,
    target_language: str,
) -> str:
    source_code = LANGUAGES[source_language]["code"]
    target_code = LANGUAGES[target_language]["code"]
    model_key = model_key_for(source_language, target_language)

    with _inference_lock:
        runtime = get_runtime(model_key)
        translated = runtime.translate(
            text,
            src_lang=source_code,
            tgt_lang=target_code,
        )

    if not isinstance(translated, str):
        raise RuntimeError("Translation runtime returned an unexpected response.")

    translated = translated.strip()
    if not translated:
        raise RuntimeError("Translation runtime returned an empty response.")

    return translated


init_cache()


@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=_active_runtime is not None,
        active_model=_active_model_key,
        supported_languages={
            code: language["name"] for code, language in LANGUAGES.items()
        },
        supported_directions=[
            "Hindi → English",
            "Hindi → Marathi",
            "English → Hindi",
            "English → Marathi",
            "Marathi → Hindi",
            "Marathi → English",
        ],
        runtime="IndicTrans2 ONNX Runtime INT8 / CPU",
    )


@app.post("/translate", response_model=TranslationResponse)
def translate(request: TranslationRequest) -> TranslationResponse:
    started = time.perf_counter()
    text = request.text.strip()
    source_language = request.source_language
    target_language = request.target_language

    if not text:
        raise HTTPException(status_code=422, detail="Text cannot be blank.")

    if source_language == target_language:
        raise HTTPException(
            status_code=422,
            detail="Source and target languages must be different.",
        )

    cached = get_cached_translation(
        text,
        source_language,
        target_language,
    )
    if cached is not None:
        return TranslationResponse(
            translated_text=cached,
            source_language=LANGUAGES[source_language]["name"],
            target_language=LANGUAGES[target_language]["name"],
            latency_ms=round((time.perf_counter() - started) * 1000),
            cached=True,
        )

    try:
        translated = translate_text(
            text,
            source_language,
            target_language,
        )
    except Exception as exc:
        logger.exception(
            "Translation failed for %s -> %s",
            source_language,
            target_language,
        )
        raise HTTPException(
            status_code=503,
            detail=(
                f"{LANGUAGES[source_language]['name']} to "
                f"{LANGUAGES[target_language]['name']} translation "
                "is currently unavailable."
            ),
        ) from exc

    save_translation(
        text,
        translated,
        source_language,
        target_language,
    )

    return TranslationResponse(
        translated_text=translated,
        source_language=LANGUAGES[source_language]["name"],
        target_language=LANGUAGES[target_language]["name"],
        latency_ms=round((time.perf_counter() - started) * 1000),
        cached=False,
    )
