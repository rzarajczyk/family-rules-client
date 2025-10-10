# -*- coding: utf-8 -*-
"""
Translation module for Family Rules Client
Handles language detection and translation loading
"""

import locale
import logging
import os

from PySide6.QtCore import QTranslator, QCoreApplication
from click import Context

from basedir import Basedir


class TranslationManager:
    """Manages application translations"""

    def __init__(self):
        self.translator = QTranslator()
        self.current_language = None

    def detect_system_language(self):
        """Detect system language and return appropriate language code"""
        try:
            # Get system locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # Extract language code (e.g., 'pl_PL' -> 'pl')
                language_code = system_locale.split('_')[0].lower()

                # Check if Polish
                if language_code == 'pl':
                    return 'pl'
                # Default to English for all other languages
                else:
                    return 'en'
            else:
                return 'en'
        except Exception:
            # Fallback to English if detection fails
            return 'en'

    def load_translation(self, language_code=None):
        """Load translation for the specified language"""
        if language_code is None:
            language_code = self.detect_system_language()

        self.current_language = language_code

        # Remove existing translator if any
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)
            self.translator = None

        # Create new translator
        self.translator = QTranslator()

        # Path to translation files
        translations_dir = os.path.join(Basedir.get_str(), "gen", "translation_files")

        # Load translation file
        translation_file = f"family_rules_{language_code}.qm"
        translation_path = os.path.join(translations_dir, translation_file)

        if os.path.exists(translation_path):
            if self.translator.load(translation_path):
                QCoreApplication.installTranslator(self.translator)
                print(f"Loaded translation: {translation_file}")
                return True
            else:
                print(f"Failed to load translation: {translation_file}")
        else:
            print(f"Translation file not found: {translation_path}")

        return False

    def get_current_language(self):
        """Get current language code"""
        return self.current_language

    def is_polish(self):
        """Check if current language is Polish"""
        return self.current_language == 'pl'


# Global translation manager instance
_translation_manager = None


def get_translation_manager():
    """Get global translation manager instance"""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager()
    return _translation_manager


def tr(text, context="MainWindow"):
    """Translation function - wrapper around QCoreApplication.translate"""
    if context:
        result = QCoreApplication.translate(context, text)
    else:
        result = QCoreApplication.translate("", text)
    logging.debug(f"Translated ≪{text}≫ as ≪{result}≫ in context {Context}")
    return result


def initialize_translations():
    """Initialize translations for the application"""
    manager = get_translation_manager()
    return manager.load_translation()
