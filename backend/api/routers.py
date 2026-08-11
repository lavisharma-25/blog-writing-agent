from fastapi import APIRouter

from backend.api.endpoints.blogs import blogs_router
from backend.api.endpoints.system import system_router


api_router = APIRouter()

api_router.include_router(system_router, tags=["System"])
api_router.include_router(blogs_router, tags=["Blogs"])
# api_router.include_router(workflow.router, tags=["Workflow"])