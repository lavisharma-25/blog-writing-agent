from fastapi import APIRouter, status

from backend.models.schema.logs import LogsResponse
from backend.models.schema.health import HealthResponse
from backend.models.schema.provider import ProvidersResponse

from backend.api.functions.get_logs import get_logs
from backend.api.functions.health import health_check
from backend.api.functions.get_providers import get_providers


system_router = APIRouter()

system_router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)(health_check)
system_router.post("/logs", response_model=LogsResponse, status_code=status.HTTP_200_OK)(get_logs)
system_router.get("/providers", response_model=ProvidersResponse, status_code=status.HTTP_200_OK)(get_providers)