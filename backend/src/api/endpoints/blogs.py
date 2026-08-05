from fastapi import APIRouter, status

from backend.src.models import schema

from backend.src.api.functions.read_blog import read_blog
from backend.src.api.functions.list_blogs import list_blogs
from backend.src.api.functions.delete_blog import delete_blog
from backend.src.api.functions.export_blog import export_blog
# from backend.src.api.functions.generate_blog import generate_blog


router = APIRouter()

# router.post("/blogs/generate", response_model=schema.WorkflowResponse, status_code=status.HTTP_200_OK)(generate_blog)
router.get("/blogs/list", response_model=schema.BlogListResponse, status_code=status.HTTP_200_OK)(list_blogs)
router.get("/blogs/{blog_id}", response_model=schema.BlogResponse, status_code=status.HTTP_200_OK)(read_blog)
router.delete("/blogs/{blog_id}", status_code=status.HTTP_200_OK)(delete_blog)
router.post("/blogs/export", status_code=status.HTTP_200_OK)(export_blog)