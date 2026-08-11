from fastapi import APIRouter, status

from backend.models.schema.list import BlogListResponse
from backend.models.schema.read import ReadBlogResponse
from backend.models.schema.delete import DeleteBlogResponse
from backend.models.schema.workflow import WorkflowResponse


from backend.api.functions.read_blog import read_blog
from backend.api.functions.list_blogs import list_blogs
from backend.api.functions.delete_blog import delete_blog
from backend.api.functions.export_blog import export_blog
from backend.api.functions.generate_blog import generate_blog


blogs_router = APIRouter()

blogs_router.post("/blogs/generate", response_model=WorkflowResponse, status_code=status.HTTP_200_OK)(generate_blog)
blogs_router.get("/blogs/list", response_model=BlogListResponse, status_code=status.HTTP_200_OK)(list_blogs)
blogs_router.post("/blogs/read", response_model=ReadBlogResponse, status_code=status.HTTP_200_OK)(read_blog)
blogs_router.delete("/blogs/delete", response_model=DeleteBlogResponse, status_code=status.HTTP_200_OK)(delete_blog)
blogs_router.post("/blogs/export", status_code=status.HTTP_200_OK)(export_blog)