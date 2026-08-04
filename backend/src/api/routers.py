from fastapi import APIRouter

from backend.src.api.endpoints import (blogs, system, workflow)


api_router = APIRouter()

api_router.include_router(system.router, tags=["System"])
api_router.include_router(blogs.router, tags=["Blogs"])
# api_router.include_router(workflow.router, tags=["Workflow"])