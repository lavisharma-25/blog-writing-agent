from fastapi import APIRouter

from backend.src.api.endpoints import health, workflow


api_router = APIRouter()

api_router.include_router(health.router, tags=["Health Check"])
api_router.include_router(workflow.router, tags=["Workflow"])