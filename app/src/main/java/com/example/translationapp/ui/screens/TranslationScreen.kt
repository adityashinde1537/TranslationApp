package com.example.translationapp.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.weight
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.SwapHoriz
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.translationapp.ui.LanguageOption
import com.example.translationapp.ui.TranslationViewModel
import com.example.translationapp.ui.supportedLanguages

@Composable
fun TranslationScreen(
    onNavigateBack: () -> Unit,
    viewModel: TranslationViewModel = viewModel()
) {
    val uiState = viewModel.uiState

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.Top
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onNavigateBack) {
                Icon(
                    imageVector = Icons.Filled.ArrowBack,
                    contentDescription = "Back"
                )
            }

            Text(
                text = "Language Translator",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(start = 8.dp)
            )
        }

        Text(
            text = "Choose languages",
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(bottom = 8.dp)
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            LanguageMenu(
                label = "From",
                selectedLanguage = uiState.sourceLanguage,
                excludedLanguageCode = uiState.targetLanguage.code,
                enabled = !uiState.isLoading,
                onSelected = viewModel::onSourceLanguageChanged,
                modifier = Modifier.weight(1f)
            )

            IconButton(
                onClick = viewModel::swapLanguages,
                enabled = !uiState.isLoading,
                modifier = Modifier.padding(top = 18.dp)
            ) {
                Icon(
                    imageVector = Icons.Filled.SwapHoriz,
                    contentDescription = "Swap languages"
                )
            }

            LanguageMenu(
                label = "To",
                selectedLanguage = uiState.targetLanguage,
                excludedLanguageCode = uiState.sourceLanguage.code,
                enabled = !uiState.isLoading,
                onSelected = viewModel::onTargetLanguageChanged,
                modifier = Modifier.weight(1f)
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text(
            text = uiState.sourceLanguage.name,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(bottom = 8.dp)
        )

        OutlinedTextField(
            value = uiState.inputText,
            onValueChange = viewModel::onInputChanged,
            placeholder = {
                Text(uiState.sourceLanguage.example)
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(140.dp),
            maxLines = 6,
            enabled = !uiState.isLoading
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = viewModel::translate,
            enabled = uiState.inputText.isNotBlank() && !uiState.isLoading,
            modifier = Modifier
                .fillMaxWidth()
                .height(50.dp)
        ) {
            if (uiState.isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.height(22.dp),
                    strokeWidth = 2.dp,
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text(
                    text = "Translate to ${uiState.targetLanguage.name}",
                    fontSize = 16.sp
                )
            }
        }

        uiState.errorMessage?.let { error ->
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = error,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodyMedium
            )
        }

        if (uiState.translatedText.isNotBlank()) {
            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = uiState.targetLanguage.name,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(bottom = 8.dp)
            )

            OutlinedTextField(
                value = uiState.translatedText,
                onValueChange = {},
                readOnly = true,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(140.dp),
                maxLines = 6
            )

            Spacer(modifier = Modifier.height(8.dp))

            val timing = uiState.latencyMs?.let { " • ${it} ms" }.orEmpty()
            Text(
                text = if (uiState.cached) {
                    "Loaded from translation cache$timing"
                } else {
                    "Generated by IndicTrans2$timing"
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Composable
private fun LanguageMenu(
    label: String,
    selectedLanguage: LanguageOption,
    excludedLanguageCode: String,
    enabled: Boolean,
    onSelected: (LanguageOption) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }

    Column(modifier = modifier) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(bottom = 4.dp)
        )

        Box {
            OutlinedButton(
                onClick = { expanded = true },
                enabled = enabled,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(selectedLanguage.name)
            }

            DropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false }
            ) {
                supportedLanguages
                    .filter { it.code != excludedLanguageCode }
                    .forEach { language ->
                        DropdownMenuItem(
                            text = { Text(language.name) },
                            onClick = {
                                expanded = false
                                onSelected(language)
                            }
                        )
                    }
            }
        }
    }
}
