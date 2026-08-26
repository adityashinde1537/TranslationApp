# Translation App

A basic Android application with Home and Translation screens built with Jetpack Compose.

## Features

- **Home Screen**: Welcome screen with navigation to Translation screen
- **Translation Screen**: 
  - Input text field for entering text to translate
  - Language selection (Spanish, French, German)
  - Translate button
  - Display translated text
  - Back navigation

## Technology Stack

- **Language**: Kotlin
- **UI Framework**: Jetpack Compose
- **Navigation**: Jetpack Compose Navigation
- **Target SDK**: Android 14 (API 34)
- **Min SDK**: Android 7.0 (API 24)

## Project Structure

```
TranslationApp/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/example/translationapp/
│   │       │   ├── MainActivity.kt
│   │       │   └── ui/
│   │       │       ├── screens/
│   │       │       │   ├── HomeScreen.kt
│   │       │       │   └── TranslationScreen.kt
│   │       │       └── theme/
│   │       │           ├── Theme.kt
│   │       │           ├── Color.kt
│   │       │           └── Type.kt
│   │       ├── res/
│   │       │   ├── values/
│   │       │   │   ├── strings.xml
│   │       │   │   └── themes.xml
│   │       │   └── mipmap/
│   │       └── AndroidManifest.xml
│   ├── build.gradle
│   └── proguard-rules.pro
├── build.gradle
├── settings.gradle
└── README.md
```

## Getting Started

1. Clone the repository
2. Open the project in Android Studio
3. Build and run the application on an emulator or physical device

## Building

```bash
./gradlew build
```

## Running

```bash
./gradlew installDebug
```

## Future Enhancements

- Integration with translation API (Google Translate, etc.)
- Translation history
- Favorites/bookmarks
- Dark mode support
- Multiple language pairs
- Text-to-speech functionality
