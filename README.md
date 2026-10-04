<div align="center">

# Translation App
### An Android translation interface built with Kotlin & Jetpack Compose

A learning project exploring declarative UI, navigation, and local state.

**Kotlin · Jetpack Compose · Material 3 · Android**

[Explore the code](app/src/main/java/com/example/translationapp) · [Report an issue](https://github.com/adityashinde1537/TranslationApp/issues)

</div>

---

## Overview

Translation App is a two-screen Android prototype with a welcome screen and an interactive translation interface. It demonstrates text input, language selection, screen navigation, and result display using Jetpack Compose.

> **Project status:** UI prototype. The Translate button currently prefixes the input with the selected language, such as `[Spanish] Hello`. A translation engine or API has not been integrated.

## Features

| Feature | Current behavior |
| --- | --- |
| Home screen | Welcome message and navigation to the translation screen |
| Text input | Multiline field for entering text |
| Language selection | Spanish, French, and German options |
| Result display | Read-only output showing the selected language and original text |
| Navigation | Forward navigation and a back button |

## Technology

| Component | Technology |
| --- | --- |
| Language | Kotlin |
| Interface | Jetpack Compose and Material 3 |
| Navigation | Navigation Compose |
| State | Compose remember and mutableStateOf |
| Android support | Android 7.0+ (minimum SDK 24) |
| Compile / target SDK | 34 |

## Getting started

1. Clone this repository:

   ```bash
   git clone https://github.com/adityashinde1537/TranslationApp.git
   ```

2. Open the project folder in Android Studio.
3. Install Android SDK 34 if prompted and sync the Gradle project.
4. Select an emulator or physical device running Android 7.0 or later.
5. Run the app configuration.

Build compatibility depends on the local Android Studio, JDK, and Gradle setup. A Gradle wrapper is not included in the current repository, so wrapper commands require adding a compatible wrapper first.

## Code guide

Key source files live in `app/src/main/java/com/example/translationapp/`:

| File or folder | Purpose |
| --- | --- |
| MainActivity.kt | Application entry point |
| ui/screens/HomeScreen.kt | Welcome screen |
| ui/screens/TranslationScreen.kt | Input, language selection, and placeholder output |
| ui/theme/ | Theme, colors, and typography |

Android configuration and dependencies are defined in `app/build.gradle`.

## Try the interface

1. Open the app and choose **Go to Translation**.
2. Enter **Hello**.
3. Select **French**, then choose **Translate**.
4. The current prototype displays **[French] Hello**.
5. Use the back button to return to the home screen.

## Planned improvements

- [ ] Connect a translation API or on-device model
- [ ] Add loading, error, and empty-input states
- [ ] Add translation history and saved phrases
- [ ] Support more language pairs
- [ ] Add text-to-speech playback
- [ ] Add screenshots and a verified build guide

These items are planned work, not implemented features.

## Feedback

Suggestions and reproducible bug reports are welcome through [GitHub Issues](https://github.com/adityashinde1537/TranslationApp/issues). Include the Android version, steps to reproduce, and expected behavior.

---

Created by [Aditya](https://github.com/adityashinde1537).
