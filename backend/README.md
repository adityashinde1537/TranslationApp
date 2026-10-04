# Translation backend

FastAPI service for Hindi `hin_Deva` → Santhali Ol Chiki `sat_Olck` translation using `facebook/nllb-200-distilled-600M`.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

The NLLB model is loaded lazily on the first uncached translation request. The initial request can take significantly longer because the model may need to download and initialize.

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
  "translated_text": "...",
  "source_language": "Hindi",
  "target_language": "Santhali (Ol Chiki)",
  "latency_ms": 1234,
  "cached": false
}
```

Translations are cached in SQLite. The cache key includes the model name and language pair, so changing models does not silently reuse incompatible results.

## Android connection

The debug Android build defaults to:

```text
http://10.0.2.2:8000/
```

That address reaches the development computer from the standard Android emulator.

For another backend address, pass a Gradle property:

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
| `MODEL_NAME` | `facebook/nllb-200-distilled-600M` | Hugging Face model |
| `TRANSLATION_CACHE_DB` | `backend/translations.db` | SQLite cache path |
| `MAX_INPUT_CHARS` | `1500` | Maximum request text length |
| `MAX_NEW_TOKENS` | `256` | Generation output limit |
| `CORS_ORIGINS` | `*` | Comma-separated allowed web origins |
| `LOG_LEVEL` | `INFO` | Python logging level |

## Accuracy note

Santhali is a low-resource language. Model output should be reviewed by fluent speakers before classroom or production use.
