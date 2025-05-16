import deepl
from deepl import Translator

from app.core.config import Settings

settings = Settings()
translator: Translator = deepl.Translator(settings.get_deepl_api_key())
