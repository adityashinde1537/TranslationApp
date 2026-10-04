package com.example.translationapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.translationapp.ui.screens.HomeScreen
import com.example.translationapp.ui.screens.TranslationScreen
import com.example.translationapp.ui.theme.TranslationAppTheme

private object Routes {
    const val HOME = "home"
    const val TRANSLATION = "translation"
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            TranslationAppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    TranslationAppNavigation()
                }
            }
        }
    }
}

@Composable
fun TranslationAppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Routes.HOME
    ) {
        composable(Routes.HOME) {
            HomeScreen(
                onNavigateToTranslation = {
                    navController.navigate(Routes.TRANSLATION) {
                        launchSingleTop = true
                    }
                }
            )
        }

        composable(Routes.TRANSLATION) {
            TranslationScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
    }
}
