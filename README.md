<div align="center">

# Hindi → Santhali TranslationApp

### Android + FastAPI translation system for Hindi to Santhali in Ol Chiki

[![Project CI](https://github.com/adityashinde1537/TranslationApp/actions/workflows/android.yml/badge.svg)](https://github.com/adityashinde1537/TranslationApp/actions/workflows/android.yml)
![Kotlin](https://img.shields.io/badge/Kotlin-1.9.0-7F52FF?logo=kotlin&logoColor=white)
![Android](https://img.shields.io/badge/Android-SDK%2034-3DDC84?logo=android&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![IndicTrans2](https://img.shields.io/badge/IndicTrans2-INT8%20ONNX-orange)

A full-stack translation prototype that sends Hindi text from an Android app to a FastAPI backend powered by IndicTrans2 and returns Santhali text in the Ol Chiki script.

[Android source](app/src/main/java/com/example/translationapp) · [Backend source](backend) · [Report a bug](https://github.com/adityashinde1537/TranslationApp/issues/new?template=bug_report.yml)

</div>

---

## What it does

1. The Android app accepts Hindi text written in Devanagari.
2. Retrofit sends the text to the backend's `POST /translate` endpoint.
3. The backend uses an INT8 ONNX export of IndicTrans2.
4. Source language is `hin_Deva`.
5. Target language is `sat_Olck`.
6. The backend validates that the result contains meaningful Ol Chiki text.
7. Completed translations are cached in SQLite.

## Real model smoke test

The previous NLLB setup failed real-output testing. The replacement IndicTrans2 model produced Ol Chiki output:

```text
नमस्ते, आप कैसे हैं?
→ ᱦᱚᱞᱮ, ᱟᱢ ᱪᱮᱫ ᱞᱮᱠᱟ?

आज मौसम अच्छा है।
→ ᱛᱮᱦᱮᱧ ᱦᱚᱭᱦᱩᱫᱤᱥ ᱱᱟᱯᱟᱭ ᱠᱟᱱᱟ ᱾
```

Named entities can still show transliteration artifacts, so native-speaker review remains necessary.

## Architecture

```text
Android app
   │
   │  POST /translate
   ▼
FastAPI backend
   │
   ├── SQLite translation cache
   │
   └── IndicTrans2 INT8 ONNX
           Hindi:    hin_Deva
           Santhali: sat_Olck
```

## Features

### Android

- Kotlin + Jetpack Compose
- Hindi → Santhali workflow
- Retrofit API client
- ViewModel-based state
- Loading and error states
- Latency display
- Cache-hit indicator
- Configurable backend URL

### Backend

- FastAPI REST API
- IndicTrans2 CPU inference through ONNX Runtime
- Lazy model download/loading
- Pinned model revision for reproducibility
- SQLite translation cache
- Ol Chiki output validation
- Health endpoint
- Input validation
- Docker support

## Tech stack

| Layer | Technology |
| --- | --- |
| Android | Kotlin + Jetpack Compose |
| Networking | Retrofit |
| Backend | Python + FastAPI |
| Translation | IndicTrans2 distilled 320M INT8 ONNX |
| Runtime | ONNX Runtime CPU |
| Source | Hindi — `hin_Deva` |
| Target | Santhali Ol Chiki — `sat_Olck` |
| Cache | SQLite |
| CI | GitHub Actions |

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

Translate:

```bash
curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"नमस्ते, आप कैसे हैं?"}'
```

See [backend/README.md](backend/README.md) for more details.

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

- Translation quality still needs native-speaker evaluation.
- Named entities may contain transliteration artifacts.
- The first request must download and initialize the model.
- The Android app still requires a reachable backend.
- The translation model is not yet running directly on-device.

## Roadmap

- [x] Hindi → Santhali Android workflow
- [x] FastAPI backend
- [x] Real Ol Chiki model output test
- [x] Replace failing NLLB pipeline with IndicTrans2
- [x] SQLite caching
- [x] Loading and error states
- [x] Android CI
- [ ] Deploy the backend to a stable HTTPS endpoint
- [ ] Add native-speaker accuracy evaluation
- [ ] Add translation history
- [ ] Add Hindi speech-to-text
- [ ] Add Santhali text-to-speech
- [ ] Explore direct on-device inference

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

---

<div align="center">

Built by [Aditya](https://github.com/adityashinde1537)

</div>
