package com.example.translationapp.data.remote

import com.google.gson.annotations.SerializedName
import retrofit2.http.Body
import retrofit2.http.POST

data class TranslationRequest(
    val text: String
)

data class TranslationResponse(
    @SerializedName("translated_text")
    val translatedText: String,
    @SerializedName("source_language")
    val sourceLanguage: String,
    @SerializedName("target_language")
    val targetLanguage: String,
    @SerializedName("latency_ms")
    val latencyMs: Long,
    val cached: Boolean
)

interface TranslationApi {
    @POST("translate")
    suspend fun translate(
        @Body request: TranslationRequest
    ): TranslationResponse
}
