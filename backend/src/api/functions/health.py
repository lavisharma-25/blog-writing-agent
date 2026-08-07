from backend.src.models import schema
from backend.src.core.logging import logger


async def health_check() -> schema.HealthResponse:
    """Return the current health status of the API."""

    logger.info("Health check requested")

    return schema.HealthResponse(
        status="healthy",
        message="API is running smoothly",
    )