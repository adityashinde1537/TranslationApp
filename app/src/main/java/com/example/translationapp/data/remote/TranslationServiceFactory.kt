package com.example.translationapp.data.remote

import com.example.translationapp.BuildConfig
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object TranslationServiceFactory {
    val api: TranslationApi by lazy {
        Retrofit.Builder()
            .baseUrl(normalizedBaseUrl())
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(TranslationApi::class.java)
    }

    private fun normalizedBaseUrl(): String {
        val configured = BuildConfig.TRANSLATION_API_BASE_URL.trim()
        return if (configured.endsWith("/")) configured else "$configured/"
    }
}
