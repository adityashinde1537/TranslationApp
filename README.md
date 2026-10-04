<div align="center">

# TranslationApp

### Modern Android translation UI prototype built with Kotlin and Jetpack Compose

[![Android CI](https://github.com/adityashinde1537/TranslationApp/actions/workflows/android.yml/badge.svg)](https://github.com/adityashinde1537/TranslationApp/actions/workflows/android.yml)
![Kotlin](https://img.shields.io/badge/Kotlin-1.9.0-7F52FF?logo=kotlin&logoColor=white)
![Android](https://img.shields.io/badge/Android-SDK%2034-3DDC84?logo=android&logoColor=white)
![Jetpack Compose](https://img.shields.io/badge/Jetpack%20Compose-1.5.4-4285F4?logo=jetpackcompose&logoColor=white)

A focused learning project for experimenting with Compose UI, navigation, state, and future translation-engine integration.

[Explore the code](app/src/main/java/com/example/translationapp) · [Report a bug](https://github.com/adityashinde1537/TranslationApp/issues/new?template=bug_report.yml)

</div>

---

## Project status

**UI prototype — translation engine not connected yet.**

The app currently demonstrates the translation workflow and returns a clearly marked preview such as `[French] Hello`. It does **not** currently perform machine translation.

## Features

- Jetpack Compose user interface
- Material 3 components
- Two-screen Navigation Compose flow
- Multiline translation input
- Target-language selection
- State preserved across configuration changes with `rememberSaveable`
- Disabled translation action for empty input
- Read-only preview result
- Light and dark theme support
- Automated Android build and unit-test workflow

## Tech stack

| Area | Technology |
| --- | --- |
| Language | Kotlin 1.9.0 |
| UI | Jetpack Compose 1.5.4 |
| Design system | Material 3 |
| Navigation | Navigation Compose 2.7.5 |
| Build | Android Gradle Plugin 8.1.0 |
| Java | JDK 17 |
| Android | minSdk 24 · targetSdk 34 · compileSdk 34 |
| CI | GitHub Actions |

## Project structure

```text
TranslationApp/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── bug_report.yml
│   └── workflows/
│       └── android.yml
├── app/
│   ├── src/main/
│   │   ├── java/com/example/translationapp/
│   │   │   ├── MainActivity.kt
│   │   │   └── ui/
│   │   │       ├── screens/
│   │   │       └── theme/
│   │   ├── res/
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── .editorconfig
├── .gitignore
├── CONTRIBUTING.md
├── gradle.properties
├── build.gradle
├── settings.gradle
└── README.md
```

## Getting started

### Requirements

- Android Studio
- JDK 17
- Android SDK 34

### Run from Android Studio

1. Clone the repository.

   ```bash
   git clone https://github.com/adityashinde1537/TranslationApp.git
   ```

2. Open the project in Android Studio.
3. Allow Gradle sync to finish.
4. Select an emulator or Android device running Android 7.0 or newer.
5. Run the `app` configuration.

### Command-line build

The repository currently expects Gradle 8.0.2 when building from the command line.

```bash
gradle --no-daemon :app:assembleDebug
```

The CI workflow provisions the required Gradle and Android SDK versions automatically.

## How it works

1. The app opens on the home screen.
2. **Start translating** navigates to the translation screen.
3. The user enters text and selects Spanish, French, or German.
4. **Translate** displays a prototype preview.
5. The interface explicitly states that no translation engine is connected.

## Current limitations

- No machine-translation API or on-device model
- No network layer
- No translation history
- No offline language model
- No text-to-speech or speech-to-text
- No persisted user preferences

## Roadmap

- [ ] Integrate a real translation engine
- [ ] Add loading and error states
- [ ] Add translation history
- [ ] Add saved phrases
- [ ] Add additional language pairs
- [ ] Add text-to-speech
- [ ] Add UI and ViewModel tests
- [ ] Add app screenshots

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

For bugs, use the repository's structured bug-report template and include reproducible steps, your Android version, and device/emulator details.

---

<div align="center">

Built by [Aditya](https://github.com/adityashinde1537)

</div>
