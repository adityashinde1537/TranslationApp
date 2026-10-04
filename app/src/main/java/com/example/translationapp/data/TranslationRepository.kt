package com.example.translationapp.data

import com.example.translationapp.data.remote.TranslationApi
import com.example.translationapp.data.remote.TranslationRequest
import com.example.translationapp.data.remote.TranslationResponse
import com.example.translationapp.data.remote.TranslationServiceFactory

class TranslationRepository(
    private val api: TranslationApi = TranslationServiceFactory.api
) {
    suspend fun translate(text: String): Result<TranslationResponse> {
        return runCatching {
            api.translate(
                TranslationRequest(text = text.trim())
            )
        }
    }
}
