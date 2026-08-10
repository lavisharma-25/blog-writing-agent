from fastapi import APIRouter, status

from backend.src.api.functions import *
from backend.src.models import schema


router = APIRouter()

router.get("/health", response_model=schema.HealthResponse, status_code=status.HTTP_200_OK)(health_check)
router.post("/logs", response_model=schema.LogsResponse, status_code=status.HTTP_200_OK)(get_logs)
router.get("/providers", response_model=schema.ProvidersResponse, status_code=status.HTTP_200_OK)(get_providers)