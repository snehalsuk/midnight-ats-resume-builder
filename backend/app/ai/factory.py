from functools import lru_cache

from app.ai.base import AIProvider, AIProviderError
from app.core.config import get_settings


@lru_cache
def get_ai_provider() -> AIProvider:
    settings = get_settings()
    if settings.ai_provider == "groq":
        from app.ai.groq_provider import GroqProvider

        return GroqProvider(api_key=settings.groq_api_key or "", model=settings.groq_model)
    # OpenAI / Anthropic / Ollama adapters plug in here later, behind the
    # same AIProvider interface, selected by settings.ai_provider.
    raise AIProviderError(f"Unsupported AI provider: {settings.ai_provider}")
