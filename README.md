<div align="center">

# Hindi → Santhali TranslationApp

### Android + FastAPI translation system for Hindi to Santhali in Ol Chiki

[![Project CI](https://github.com/adityashinde1537/TranslationApp/actions/workflows/android.yml/badge.svg)](https://github.com/adityashinde1537/TranslationApp/actions/workflows/android.yml)
![Kotlin](https://img.shields.io/badge/Kotlin-1.9.0-7F52FF?logo=kotlin&logoColor=white)
![Android](https://img.shields.io/badge/Android-SDK%2034-3DDC84?logo=android&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![NLLB](https://img.shields.io/badge/NLLB-200-orange)

A full-stack translation prototype that sends Hindi text from an Android app to a FastAPI backend powered by Meta's NLLB model and returns Santhali text in the Ol Chiki script.

[Android source](app/src/main/java/com/example/translationapp) · [Backend source](backend) · [Report a bug](https://github.com/adityashinde1537/TranslationApp/issues/new?template=bug_report.yml)

</div>

---

## What it does

1. The Android app accepts Hindi text written in Devanagari.
2. Retrofit sends the text to the backend's `POST /translate` endpoint.
3. The backend uses `facebook/nllb-200-distilled-600M`.
4. Source language is configured as `hin_Deva`.
5. Target language is configured as `sat_Olck`.
6. The backend returns Santhali in Ol Chiki.
7. Completed translations are cached in SQLite for faster repeated requests.

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
   └── NLLB-200 distilled 600M
           Hindi:    hin_Deva
           Santhali: sat_Olck
```

## Features

### Android

- Kotlin + Jetpack Compose UI
- Hindi → Santhali focused workflow
- Retrofit API client
- ViewModel-based translation state
- Loading and error states
- Result latency display
- Cache-hit indicator
- Configurable backend base URL
- Cleartext HTTP enabled only for debug builds

### Backend

- FastAPI REST API
- NLLB sequence-to-sequence translation
- Lazy model loading
- CUDA support when available
- SQLite translation cache
- Health endpoint
- Input length validation
- Serialized inference to reduce memory spikes
- Docker support

## Tech stack

| Layer | Technology |
| --- | --- |
| Android language | Kotlin 1.9.0 |
| Android UI | Jetpack Compose 1.5.4 + Material 3 |
| Android networking | Retrofit 2.9.0 |
| Android state | ViewModel + Compose state |
| Backend | Python + FastAPI |
| Translation model | `facebook/nllb-200-distilled-600M` |
| Source language | Hindi — `hin_Deva` |
| Target language | Santhali Ol Chiki — `sat_Olck` |
| Cache | SQLite |
| CI | GitHub Actions |

## Repository structure

```text
TranslationApp/
├── app/
│   ├── build.gradle
│   └── src/main/
│       ├── AndroidManifest.xml
│       └── java/com/example/translationapp/
│           ├── MainActivity.kt
│           ├── data/
│           │   ├── TranslationRepository.kt
│           │   └── remote/
│           └── ui/
│               ├── TranslationViewModel.kt
│               ├── screens/
│               └── theme/
├── backend/
│   ├── Dockerfile
│   ├── README.md
│   ├── main.py
│   └── requirements.txt
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── CONTRIBUTING.md
└── README.md
```

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

On the first uncached translation, the backend may need to download and initialize the model.

Check the service:

```bash
curl http://127.0.0.1:8000/health
```

Translate:

```bash
curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"नमस्ते, आप कैसे हैं?"}'
```

See [backend/README.md](backend/README.md) for Docker and environment-variable configuration.

## Run the Android app

### Requirements

- Android Studio
- JDK 17
- Android SDK 34
- Running translation backend

The debug build defaults to:

```text
http://10.0.2.2:8000/
```

This is the Android emulator address for a backend running on the development computer.

To use another backend URL:

```bash
gradle :app:assembleDebug \
  -PTRANSLATION_API_BASE_URL=http://192.168.1.10:8000/
```

For production, use an HTTPS backend URL. Release builds disable cleartext HTTP.

## API contract

### `POST /translate`

Request:

```json
{
  "text": "नमस्ते, आप कैसे हैं?"
}
```

Response:

```json
{
  "translated_text": "...",
  "source_language": "Hindi",
  "target_language": "Santhali (Ol Chiki)",
  "latency_ms": 1234,
  "cached": false
}
```

### `GET /health`

Reports the configured model, language codes, device, and whether the NLLB model has already been loaded.

## Current limitations

- Translation quality depends on NLLB performance for this low-resource language pair.
- First-run model download and initialization can be slow.
- CPU inference may not meet a sub-3-second latency target.
- The Android app still requires the backend to be reachable; the NLLB model is not running directly on-device.
- Classroom or production output should be reviewed by fluent Santhali speakers.

## Roadmap

- [x] Hindi → Santhali Android workflow
- [x] FastAPI translation backend
- [x] NLLB integration
- [x] SQLite caching
- [x] Loading and error states
- [x] Android CI
- [ ] Deploy the backend to a stable HTTPS endpoint
- [ ] Add translation history
- [ ] Add speech-to-text for Hindi
- [ ] Add Santhali text-to-speech
- [ ] Evaluate accuracy with native-speaker test data
- [ ] Explore an optimized on-device model for offline use

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

---

<div align="center">

Built by [Aditya](https://github.com/adityashinde1537)

</div>
