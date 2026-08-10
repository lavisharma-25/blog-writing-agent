from fastapi import APIRouter

from backend.api import endpoints


api_router = APIRouter()

api_router.include_router(endpoints.system_router, tags=["System"])
api_router.include_router(endpoints.blogs_router, tags=["Blogs"])
# api_router.include_router(workflow.router, tags=["Workflow"])