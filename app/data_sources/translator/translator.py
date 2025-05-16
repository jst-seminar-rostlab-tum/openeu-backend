import re
from typing import cast

from deepl import TextResult, Translator


class TextPreprocessor:
    """Utility to clean and optimize input text before translation."""

    @staticmethod
    def clean(text: str) -> str:
        # Basic pre-cleaning steps to reduce character count
        text = re.sub(r"<[^>]+>", "", text)  # Remove HTML
        text = re.sub(r"\s+", " ", text)  # Collapse whitespace
        text = re.sub(r"[.]{3,}", "...", text)  # Normalize ellipsis
        text = text.strip()
        return text


class DeepLTranslator:
    """
    Translates arbitrary text to English using DeepL.

    Applies basic pre-cleaning to reduce character count and optimize API usage.

    DeepL API usage constraints:
    - Header size: max 16 KiB
    - Request size: max 128 KiB
    - Free tier: 500,000 characters/month
    """

    def __init__(self, deepl_translator: Translator):
        self.translator = deepl_translator

    def translate(self, text: str) -> TextResult:
        cleaned_text = TextPreprocessor.clean(text)
        result = self.translator.translate_text(cleaned_text, target_lang="EN-US")
        return cast(TextResult, result)
