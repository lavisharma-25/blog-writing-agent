import uvicorn

from backend.src.core.settings import settings


if __name__ == "__main__":
    uvicorn.run(
        "backend.src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.RELOAD,
    )
