from fastapi import APIRouter, status

from backend.api import functions
from backend.models import schema


blogs_router = APIRouter()

blogs_router.post("/blogs/generate", response_model=schema.WorkflowResponse, status_code=status.HTTP_200_OK)(functions.generate_blog)
blogs_router.get("/blogs/list", response_model=schema.BlogListResponse, status_code=status.HTTP_200_OK)(functions.list_blogs)
blogs_router.post("/blogs/read", response_model=schema.ReadBlogResponse, status_code=status.HTTP_200_OK)(functions.read_blog)
blogs_router.delete("/blogs/delete", response_model=schema.DeleteBlogResponse, status_code=status.HTTP_200_OK)(functions.delete_blog)
blogs_router.post("/blogs/export", status_code=status.HTTP_200_OK)(functions.export_blog)