from fastapi import APIRouter, status

from backend.api import functions
from backend.models import schema


system_router = APIRouter()

system_router.get("/health", response_model=schema.HealthResponse, status_code=status.HTTP_200_OK)(functions.health_check)
system_router.post("/logs", response_model=schema.LogsResponse, status_code=status.HTTP_200_OK)(functions.get_logs)
system_router.get("/providers", response_model=schema.ProvidersResponse, status_code=status.HTTP_200_OK)(functions.get_providers)