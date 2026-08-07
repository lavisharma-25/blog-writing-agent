from fastapi import APIRouter, status

from backend.src.models import schema
from backend.src.api.functions.get_logs import get_logs
from backend.src.api.functions.health import health_check
from backend.src.api.functions.get_providers import get_providers


router = APIRouter()

router.get("/health", response_model=schema.HealthResponse, status_code=status.HTTP_200_OK)(health_check)
router.post("/logs", response_model=schema.LogsResponse, status_code=status.HTTP_200_OK)(get_logs)
router.get("/providers", response_model=schema.ProvidersResponse, status_code=status.HTTP_200_OK)(get_providers)