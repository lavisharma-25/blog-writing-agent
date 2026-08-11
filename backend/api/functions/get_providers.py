from backend.core.settings import settings
from backend.models.schema.provider import ProvidersResponse


async def get_providers() -> ProvidersResponse:

    custom_provider = settings.CUSTOM_PROVIDER if settings.CUSTOM_PROVIDER != "None" else None

    resolved_openai = settings.resolve_openai_config()

    return ProvidersResponse(
        status="success",
        data={
            "active_provider": settings.LLM_PROVIDER,
            "custom_provider": custom_provider,
            "providers": {
                "openai": {"model": settings.OPENAI_MODEL, "base_url": settings.OPENAI_BASE_URL},
                "gemini": {"model": settings.GOOGLE_MODEL, "location": settings.GOOGLE_CLOUD_LOCATION},
                "openrouter": {"model": settings.OPENROUTER_MODEL},
            },
            "custom_openai_slot": {
                "model": resolved_openai.get("model"),
                "base_url": resolved_openai.get("base_url"),
            },
        },
    )