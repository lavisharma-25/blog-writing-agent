from fastapi import APIRouter, status

from backend.src.api.functions.get_logs import get_logs
from backend.src.api.functions.health import health_check
from backend.src.api.functions.get_providers import get_providers

from backend.src.models.schema import ProvidersResponse


router = APIRouter()

router.get("/health", status_code=status.HTTP_200_OK)(health_check)
router.post("/logs", status_code=status.HTTP_200_OK)(get_logs)
router.get("/providers", response_model=ProvidersResponse, status_code=status.HTTP_200_OK)(get_providers)