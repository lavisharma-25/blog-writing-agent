from backend.src.core.logging import logger

async def health_check():
    """Return the current health status of the API."""

    logger.info("Health check requested")

    return {
        "status": "healthy",
        "service": "Blog Writing Agenti API",
    }