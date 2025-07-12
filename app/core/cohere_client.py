from app.core.config import Settings
import cohere
from cohere import ClientV2


settings = Settings()
co: ClientV2 = cohere.ClientV2(api_key=settings.get_cohere_api_key("COHERE_API_KEY"))
