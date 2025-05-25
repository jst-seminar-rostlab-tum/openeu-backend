from app.core.config import Settings
from openai import OpenAI

EMBED_MODEL = "text-embedding-ada-002"
EMBED_DIM = 1536
MAX_TOKENS = 500
BATCH_SZ = 100

settings = Settings()
openai = OpenAI(api_key=settings.get_openai_api_key())
