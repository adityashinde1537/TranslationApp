package com.example.translationapp.ui

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.translationapp.data.TranslationRepository
import java.io.IOException
import kotlinx.coroutines.launch
import retrofit2.HttpException

data class LanguageOption(
    val code: String,
    val name: String,
    val example: String
)

val supportedLanguages = listOf(
    LanguageOption(
        code = "hi",
        name = "Hindi",
        example = "उदाहरण: नमस्ते, आप कैसे हैं?"
    ),
    LanguageOption(
        code = "en",
        name = "English",
        example = "Example: Hello, how are you?"
    ),
    LanguageOption(
        code = "mr",
        name = "Marathi",
        example = "उदाहरण: नमस्कार, तुम्ही कसे आहात?"
    )
)

data class TranslationUiState(
    val inputText: String = "",
    val translatedText: String = "",
    val sourceLanguage: LanguageOption = supportedLanguages.first { it.code == "hi" },
    val targetLanguage: LanguageOption = supportedLanguages.first { it.code == "en" },
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val latencyMs: Long? = null,
    val cached: Boolean = false
)

class TranslationViewModel : ViewModel() {
    private val repository = TranslationRepository()

    var uiState by mutableStateOf(TranslationUiState())
        private set

    fun onInputChanged(value: String) {
        uiState = uiState.copy(
            inputText = value,
            translatedText = "",
            errorMessage = null,
            latencyMs = null,
            cached = false
        )
    }

    fun onSourceLanguageChanged(language: LanguageOption) {
        uiState = if (language.code == uiState.targetLanguage.code) {
            uiState.copy(
                sourceLanguage = language,
                targetLanguage = uiState.sourceLanguage,
                translatedText = "",
                errorMessage = null,
                latencyMs = null,
                cached = false
            )
        } else {
            uiState.copy(
                sourceLanguage = language,
                translatedText = "",
                errorMessage = null,
                latencyMs = null,
                cached = false
            )
        }
    }

    fun onTargetLanguageChanged(language: LanguageOption) {
        uiState = if (language.code == uiState.sourceLanguage.code) {
            uiState.copy(
                sourceLanguage = uiState.targetLanguage,
                targetLanguage = language,
                translatedText = "",
                errorMessage = null,
                latencyMs = null,
                cached = false
            )
        } else {
            uiState.copy(
                targetLanguage = language,
                translatedText = "",
                errorMessage = null,
                latencyMs = null,
                cached = false
            )
        }
    }

    fun swapLanguages() {
        uiState = uiState.copy(
            sourceLanguage = uiState.targetLanguage,
            targetLanguage = uiState.sourceLanguage,
            translatedText = "",
            errorMessage = null,
            latencyMs = null,
            cached = false
        )
    }

    fun translate() {
        val text = uiState.inputText.trim()
        if (text.isEmpty() || uiState.isLoading) return

        val sourceLanguage = uiState.sourceLanguage.code
        val targetLanguage = uiState.targetLanguage.code

        viewModelScope.launch {
            uiState = uiState.copy(
                isLoading = true,
                translatedText = "",
                errorMessage = null,
                latencyMs = null,
                cached = false
            )

            repository.translate(
                text = text,
                sourceLanguage = sourceLanguage,
                targetLanguage = targetLanguage
            )
                .onSuccess { response ->
                    uiState = uiState.copy(
                        translatedText = response.translatedText,
                        isLoading = false,
                        latencyMs = response.latencyMs,
                        cached = response.cached
                    )
                }
                .onFailure { error ->
                    uiState = uiState.copy(
                        isLoading = false,
                        errorMessage = error.toUserMessage()
                    )
                }
        }
    }

    private fun Throwable.toUserMessage(): String {
        return when (this) {
            is IOException ->
                "Cannot reach the translation service. Check that the FastAPI backend is running."
            is HttpException ->
                "Translation service returned an error (${code()})."
            else ->
                message?.takeIf { it.isNotBlank() } ?: "Translation failed. Please try again."
        }
    }
}
