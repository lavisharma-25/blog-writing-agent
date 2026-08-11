from backend.core.logging import logger
from backend.models.schema.health import HealthResponse


async def health_check() -> HealthResponse:
    """Return the current health status of the API."""

    logger.info("Health check requested")

    return HealthResponse(
        status="success",
        message="API is running smoothly",
    )