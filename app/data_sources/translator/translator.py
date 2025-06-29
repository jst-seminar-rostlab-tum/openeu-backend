import re
from langdetect import detect, LangDetectException

from app.services.llm_service.llm_client import LLMClient
from app.services.llm_service.llm_models import LLMModels
import logging

logger = logging.getLogger(__name__)

base_prompt = (
    "You are a professional translator. Translate "
    "the following text to English, "
    "without adding or removing meaning. Do not "
    "assume facts not present in the original "
    "text. Keep the translation as neutral and "
    "faithful as possible.\n\n{content}"
)


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


class Translator:
    """
    A service to translate text to English using an LLM.
    """

    def __init__(self, prod: bool = False):
        """
        Initialize the translator.

        :param prod: Flag to indicate whether translations should be performed (True for production).
        """
        self.prod = prod

    def translate(self, text: str) -> str:
        """
        Translates a single string of text into English.

        If the text is already in English or translation fails, the original
        text is returned.

        Args:
            :param text: The text to translate (e.g., a title or description).
            :param self: The instance of the Translator class.

        Returns:
            str: The translated English text, or the original text.
        """
        if not text or not text.strip() or not self.prod:
            return text

        text = TextPreprocessor.clean(text)

        try:
            detected_lang = detect(text)
            if detected_lang == "en":
                return text
        except LangDetectException:
            logger.warning("Language detection failed for text, proceeding with translation attempt.")

        try:
            prompt = base_prompt.format(content=text)
            llm_client = LLMClient(model=LLMModels.openai_4o_mini)
            translated_text = llm_client.generate_response(prompt)
            return translated_text
        except Exception as e:
            logger.error(f"Translation failed due to an error: {e}")
            return text
