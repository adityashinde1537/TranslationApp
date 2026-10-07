<div align="center">

# TranslationApp

### Hindi ↔ English ↔ Marathi Android translation app

[![Project CI](https://github.com/adityashinde1537/TranslationApp/actions/workflows/android.yml/badge.svg)](https://github.com/adityashinde1537/TranslationApp/actions/workflows/android.yml)
![Kotlin](https://img.shields.io/badge/Kotlin-1.9.0-7F52FF?logo=kotlin&logoColor=white)
![Android](https://img.shields.io/badge/Android-SDK%2034-3DDC84?logo=android&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![IndicTrans2](https://img.shields.io/badge/IndicTrans2-INT8%20ONNX-orange)

A full-stack Android translation project for Hindi, English and Marathi using a FastAPI backend, IndicTrans2 ONNX models and SQLite result caching.

[Android source](app/src/main/java/com/example/translationapp) · [Backend source](backend) · [Report a bug](https://github.com/adityashinde1537/TranslationApp/issues/new?template=bug_report.yml)

</div>

---

## Supported translations

- Hindi → English
- Hindi → Marathi
- English → Hindi
- English → Marathi
- Marathi → Hindi
- Marathi → English

The Android app includes source and target language selectors plus a one-tap swap button.

## Architecture

```text
Android app
   │
   │  POST /translate
   │  text + source_language + target_language
   ▼
FastAPI backend
   │
   ├── SQLite translation cache
   │
   └── IndicTrans2 INT8 ONNX
         ├── English → Indic
         ├── Indic → English
         └── Indic → Indic
```

Language codes used by the models:

| Language | API code | IndicTrans2 code |
| --- | --- | --- |
| Hindi | `hi` | `hin_Deva` |
| English | `en` | `eng_Latn` |
| Marathi | `mr` | `mar_Deva` |

## Features

### Android

- Kotlin + Jetpack Compose
- Hindi, English and Marathi selectors
- Six translation directions
- One-tap language swap
- Retrofit API client
- ViewModel-based UI state
- Loading and error states
- Latency display
- Cache-hit indicator
- Configurable backend URL

### Backend

- FastAPI REST API
- IndicTrans2 CPU inference through ONNX Runtime
- Automatic model selection by translation direction
- Lazy model loading to reduce memory usage
- SQLite translation cache
- Health endpoint
- Input and language validation
- Docker support

## Translation models

The backend uses three INT8 ONNX model families:

- `hari31416/indictrans2-en-indic-dist-200M-ONNX-int8`
- `hari31416/indictrans2-indic-en-dist-200M-ONNX-int8`
- `hari31416/indictrans2-indic-indic-dist-320M-ONNX-int8`

Only the model needed for the current direction is kept active in memory.

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then check:

```bash
curl http://127.0.0.1:8000/health
```

Example translation:

```bash
curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"नमस्ते","source_language":"hi","target_language":"en"}'
```

See [backend/README.md](backend/README.md) for backend details.

## Run the Android app

The debug build defaults to:

```text
http://10.0.2.2:8000/
```

To use another backend URL:

```bash
gradle :app:assembleDebug \
  -PTRANSLATION_API_BASE_URL=http://192.168.1.10:8000/
```

For production, use HTTPS.

## Current limitations

- The first request for a model direction must download and initialize that model.
- Switching between English→Indic, Indic→English and Indic→Indic can require loading a different model.
- Translation quality should be reviewed before high-stakes or production use.
- The Android app requires a reachable backend.
- Models are not yet running directly on-device.

## Roadmap

- [x] Hindi ↔ English translation
- [x] Hindi ↔ Marathi translation
- [x] English ↔ Marathi translation
- [x] FastAPI backend
- [x] IndicTrans2 ONNX inference
- [x] SQLite caching
- [x] Loading and error states
- [x] Android CI
- [ ] Add translation history
- [ ] Add speech-to-text
- [ ] Add text-to-speech
- [ ] Explore direct on-device inference

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

---

<div align="center">

Built by [Aditya](https://github.com/adityashinde1537)

</div>
