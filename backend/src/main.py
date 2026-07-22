from fastapi import FastAPI

from backend.src.api.routers import api_router
from backend.src.core.settings import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(api_router, prefix="/api/v1")