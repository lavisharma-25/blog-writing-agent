from fastapi import APIRouter, status

from backend.src.api.functions import *
from backend.src.models import schema


router = APIRouter()

router.post("/blogs/generate", response_model=schema.WorkflowResponse, status_code=status.HTTP_200_OK)(generate_blog)
router.get("/blogs/list", response_model=schema.BlogListResponse, status_code=status.HTTP_200_OK)(list_blogs)
router.post("/blogs/read", response_model=schema.ReadBlogResponse, status_code=status.HTTP_200_OK)(read_blog)
router.delete("/blogs/delete", response_model=schema.DeleteBlogResponse, status_code=status.HTTP_200_OK)(delete_blog)
router.post("/blogs/export", status_code=status.HTTP_200_OK)(export_blog)