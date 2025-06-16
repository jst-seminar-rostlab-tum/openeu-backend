from openai import OpenAI

from app.core.config import Settings

EMBED_MODEL = "text-embedding-ada-002"
EMBED_DIM = 1536
MAX_TOKENS = 1000
BATCH_SZ = 100

settings = Settings()
openai = OpenAI(api_key=settings.get_openai_api_key())
