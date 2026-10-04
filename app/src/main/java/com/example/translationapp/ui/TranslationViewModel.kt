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

data class TranslationUiState(
    val inputText: String = "",
    val translatedText: String = "",
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

    fun translate() {
        val text = uiState.inputText.trim()
        if (text.isEmpty() || uiState.isLoading) return

        viewModelScope.launch {
            uiState = uiState.copy(
                isLoading = true,
                translatedText = "",
                errorMessage = null,
                latencyMs = null,
                cached = false
            )

            repository.translate(text)
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
