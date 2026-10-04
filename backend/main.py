import hashlib
import logging
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = os.getenv("MODEL_NAME", "facebook/nllb-200-distilled-600M")
SOURCE_LANGUAGE_CODE = "hin_Deva"
TARGET_LANGUAGE_CODE = "sat_Olck"
SOURCE_LANGUAGE_NAME = "Hindi"
TARGET_LANGUAGE_NAME = "Santhali (Ol Chiki)"
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "1500"))
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "256"))

DEFAULT_CACHE_PATH = Path(__file__).resolve().parent / "translations.db"
CACHE_DB_PATH = Path(os.getenv("TRANSLATION_CACHE_DB", str(DEFAULT_CACHE_PATH)))

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("translation-backend")

app = FastAPI(
    title="Hindi to Santhali Translation API",
    version="1.0.0",
    description="NLLB-powered Hindi to Santhali (Ol Chiki) translation service.",
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
_tokenizer: Any | None = None
_target_token_id: int | None = None
_runtime_lock = threading.Lock()
_inference_lock = threading.Lock()

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


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
    model_loaded: bool
    source_language_code: str
    target_language_code: str
    device: str


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
                    MODEL_NAME,
                    SOURCE_LANGUAGE_CODE,
                    TARGET_LANGUAGE_CODE,
                ),
            )
            connection.commit()
    except sqlite3.Error:
        logger.exception("Translation cache write failed")


def get_runtime() -> tuple[Any, Any, int]:
    global _model, _tokenizer, _target_token_id

    if _model is not None and _tokenizer is not None and _target_token_id is not None:
        return _model, _tokenizer, _target_token_id

    with _runtime_lock:
        if _model is None or _tokenizer is None or _target_token_id is None:
            logger.info("Loading translation model %s on %s", MODEL_NAME, DEVICE)

            tokenizer = AutoTokenizer.from_pretrained(
                MODEL_NAME,
                src_lang=SOURCE_LANGUAGE_CODE,
                tgt_lang=TARGET_LANGUAGE_CODE,
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
            model.to(DEVICE)
            model.eval()

            target_token_id = tokenizer.convert_tokens_to_ids(TARGET_LANGUAGE_CODE)
            if target_token_id is None or target_token_id == tokenizer.unk_token_id:
                raise RuntimeError(
                    f"Target language token {TARGET_LANGUAGE_CODE} is unavailable."
                )

            _tokenizer = tokenizer
            _model = model
            _target_token_id = int(target_token_id)

            logger.info("Translation model loaded")

    return _model, _tokenizer, _target_token_id


def translate_text(text: str) -> str:
    model, tokenizer, target_token_id = get_runtime()

    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    ).to(DEVICE)

    with _inference_lock, torch.inference_mode():
        generated = model.generate(
            **encoded,
            forced_bos_token_id=target_token_id,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=1,
        )

    return tokenizer.batch_decode(
        generated,
        skip_special_tokens=True,
    )[0].strip()


init_cache()


@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model=MODEL_NAME,
        model_loaded=_model is not None,
        source_language_code=SOURCE_LANGUAGE_CODE,
        target_language_code=TARGET_LANGUAGE_CODE,
        device=str(DEVICE),
    )


@app.post("/translate", response_model=TranslationResponse)
def translate(request: TranslationRequest) -> TranslationResponse:
    started = time.perf_counter()
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=422, detail="Text cannot be blank.")

    cached = get_cached_translation(text)
    if cached is not None:
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
            detail="Translation model is unavailable.",
        ) from exc

    if not translated:
        raise HTTPException(
            status_code=500,
            detail="The model returned an empty translation.",
        )

    save_translation(text, translated)

    return TranslationResponse(
        translated_text=translated,
        latency_ms=round((time.perf_counter() - started) * 1000),
        cached=False,
    )
