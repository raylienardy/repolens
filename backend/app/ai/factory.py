from app.ai.provider import AIProvider
from app.ai.providers.mock import MockProvider
from app.core.config import settings

_REGISTRY: dict[str, type] = {
    "mock": MockProvider,
}

def get_provider() -> AIProvider:
    provider_name = (settings.AI_PROVIDER or "mock").lower()
    provider_cls = _REGISTRY.get(provider_name)
    if provider_cls is None:
        supported = ", ".join(sorted(_REGISTRY))
        raise ValueError(
            f"Unknown AI provider '{provider_name}'. Supported providers: {supported}. "
            "Implementasi provider konkret menyusul di Phase 7b."
        )
    return provider_cls()
