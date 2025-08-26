"""
Localization system for FAPS Knowledge Assistant
"""
import json
import os
from typing import Dict, Any
from src.config import settings


class Localization:
    def __init__(self):
        self.current_language = settings.default_language
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load all available translations"""
        locales_dir = "locales"
        if os.path.exists(locales_dir):
            for lang_dir in os.listdir(locales_dir):
                lang_path = os.path.join(locales_dir, lang_dir)
                if os.path.isdir(lang_path):
                    self.translations[lang_dir] = {}
                    for file in os.listdir(lang_path):
                        if file.endswith('.json'):
                            file_path = os.path.join(lang_path, file)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                namespace = file[:-5]  # Remove .json extension
                                self.translations[lang_dir][namespace] = json.load(f)
    
    def set_language(self, language: str):
        """Set the current language"""
        if language in self.translations:
            self.current_language = language
    
    def get_text(self, key: str, namespace: str = "ui") -> str:
        """Get translated text for a key"""
        try:
            return self.translations[self.current_language][namespace][key]
        except KeyError:
            # Fallback to default language
            try:
                return self.translations[settings.default_language][namespace][key]
            except KeyError:
                return key  # Return the key itself if no translation found
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available languages"""
        language_names = {
            "de": "Deutsch",
            "en": "English"
        }
        return {lang: language_names.get(lang, lang) for lang in self.translations.keys()}


# Global localization instance
localization = Localization()