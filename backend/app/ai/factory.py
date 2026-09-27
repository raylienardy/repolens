from app.ai.provider import AIProvider
from app.ai.providers.mock import MockProvider
from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import settings

_REGISTRY: dict[str, type] = {
    "mock": MockProvider,
    "openai_compatible": OpenAICompatibleProvider,
}

_REQUIRED_SETTINGS: dict[str, tuple[str, ...]] = {
    "openai_compatible": ("AI_API_KEY", "AI_BASE_URL", "AI_MODEL"),
}


def get_provider() -> AIProvider:
    provider_name = (settings.AI_PROVIDER or "mock").lower()
    provider_cls = _REGISTRY.get(provider_name)
    if provider_cls is None:
        supported = ", ".join(sorted(_REGISTRY))
        raise ValueError(
            f"Unknown AI provider '{provider_name}'. Supported providers: {supported}."
        )

    required = _REQUIRED_SETTINGS.get(provider_name, ())
    missing = [name for name in required if not getattr(settings, name, None)]
    if missing:
        raise ValueError(
            f"Provider '{provider_name}' is missing required setting(s): {', '.join(missing)}."
        )
    if provider_name == "openai_compatible":
        return OpenAICompatibleProvider(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
            model=settings.AI_MODEL,
        )
    return provider_cls()

