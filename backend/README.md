# Translation backend

FastAPI service for translating between Hindi, English and Marathi.

## Supported directions

- Hindi → English
- Hindi → Marathi
- English → Hindi
- English → Marathi
- Marathi → Hindi
- Marathi → English

## Models

The backend automatically selects the correct INT8 ONNX IndicTrans2 model:

| Direction type | Model |
| --- | --- |
| English → Hindi/Marathi | `hari31416/indictrans2-en-indic-dist-200M-ONNX-int8` |
| Hindi/Marathi → English | `hari31416/indictrans2-indic-en-dist-200M-ONNX-int8` |
| Hindi ↔ Marathi | `hari31416/indictrans2-indic-indic-dist-320M-ONNX-int8` |

Only one model is kept active at a time to reduce memory usage.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Models are downloaded lazily on the first request that needs each direction family.

## Endpoints

### Health

```http
GET /health
```

### Translate

```http
POST /translate
Content-Type: application/json
```

Request:

```json
{
  "text": "नमस्ते",
  "source_language": "hi",
  "target_language": "en"
}
```

Allowed language codes are:

- `hi` — Hindi
- `en` — English
- `mr` — Marathi

Response shape:

```json
{
  "translated_text": "Hello",
  "source_language": "Hindi",
  "target_language": "English",
  "latency_ms": 123,
  "cached": false
}
```

Translations are cached in SQLite. The cache key includes the model name, revision, source language, target language and input text.

## Android connection

The debug Android build defaults to:

```text
http://10.0.2.2:8000/
```

For another backend address:

```bash
gradle :app:assembleDebug -PTRANSLATION_API_BASE_URL=http://192.168.1.10:8000/
```

Release builds disable cleartext HTTP, so production deployments should use HTTPS.

## Docker

```bash
docker build -t translationapp-backend .
docker run --rm -p 8000:8000 -v hf-cache:/model-cache translationapp-backend
```

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `INDIC_INDIC_MODEL_NAME` | IndicTrans2 Indic→Indic INT8 model | Hindi ↔ Marathi model |
| `INDIC_INDIC_MODEL_REVISION` | pinned commit | Indic→Indic revision |
| `EN_INDIC_MODEL_NAME` | IndicTrans2 English→Indic INT8 model | English → Hindi/Marathi model |
| `EN_INDIC_MODEL_REVISION` | `main` | English→Indic revision |
| `INDIC_EN_MODEL_NAME` | IndicTrans2 Indic→English INT8 model | Hindi/Marathi → English model |
| `INDIC_EN_MODEL_REVISION` | `main` | Indic→English revision |
| `TRANSLATION_CACHE_DB` | `backend/translations.db` | SQLite cache path |
| `MAX_INPUT_CHARS` | `1500` | Maximum request text length |
| `CORS_ORIGINS` | `*` | Comma-separated allowed web origins |
| `LOG_LEVEL` | `INFO` | Python logging level |

## Accuracy note

Machine translation can make mistakes, especially with names, mixed-language text and unusual phrasing. Review important translations before relying on them.
