# Translation backend

FastAPI service for Hindi `hin_Deva` → Santhali Ol Chiki `sat_Olck` translation.

The backend uses the public INT8 ONNX export:

`hari31416/indictrans2-indic-indic-dist-320M-ONNX-int8`

This model is derived from AI4Bharat IndicTrans2 and is designed for CPU inference.

## Why IndicTrans2

The earlier NLLB prototype compiled correctly but failed real Hindi → Santhali output testing. The replacement IndicTrans2 smoke test produced genuine Ol Chiki output for all test sentences.

Example:

```text
Hindi:    नमस्ते, आप कैसे हैं?
Santhali: ᱦᱚᱞᱮ, ᱟᱢ ᱪᱮᱫ ᱞᱮᱠᱟ?
```

Named entities can still contain transliteration artifacts, so classroom output should be reviewed by fluent speakers.

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

The model is downloaded lazily on the first uncached translation request.

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
  "text": "नमस्ते, आप कैसे हैं?"
}
```

Response shape:

```json
{
  "translated_text": "ᱦᱚᱞᱮ, ᱟᱢ ᱪᱮᱫ ᱞᱮᱠᱟ?",
  "source_language": "Hindi",
  "target_language": "Santhali (Ol Chiki)",
  "latency_ms": 123,
  "cached": false
}
```

Translations are cached in SQLite. The cache key includes the model revision, so model upgrades do not reuse stale translations.

The backend also checks that generated output contains a meaningful amount of Ol Chiki text before caching or returning it.

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
docker build -t hindi-santhali-backend .
docker run --rm -p 8000:8000 -v hf-cache:/model-cache hindi-santhali-backend
```

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `MODEL_NAME` | `hari31416/indictrans2-indic-indic-dist-320M-ONNX-int8` | Hugging Face ONNX model |
| `MODEL_REVISION` | pinned commit | Reproducible model snapshot |
| `TRANSLATION_CACHE_DB` | `backend/translations.db` | SQLite cache path |
| `MAX_INPUT_CHARS` | `1500` | Maximum request text length |
| `MIN_OL_CHIKI_RATIO` | `0.50` | Minimum Ol Chiki letter ratio |
| `CORS_ORIGINS` | `*` | Comma-separated allowed web origins |
| `LOG_LEVEL` | `INFO` | Python logging level |

## Accuracy note

Santali is a low-resource language. The model now produces real Ol Chiki output, but translation quality and named-entity handling still require native-speaker evaluation before classroom or production use.
