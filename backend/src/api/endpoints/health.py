from fastapi import APIRouter

from backend.src.api.functions.health import health_check

router = APIRouter()

router.get("/health")(health_check)