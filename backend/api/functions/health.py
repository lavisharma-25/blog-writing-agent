from backend.models import schema
from backend.core.logging import logger


async def health_check() -> schema.HealthResponse:
    """Return the current health status of the API."""

    logger.info("Health check requested")

    return schema.HealthResponse(
        status="success",
        message="API is running smoothly",
    )