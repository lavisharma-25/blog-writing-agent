from fastapi import HTTPException

from backend.services.blog_service import read_blog_data
from backend.models.schema.read import ReadBlogRequest, ReadBlogResponse


def read_blog(request: ReadBlogRequest) -> ReadBlogResponse:
    try:
        return ReadBlogResponse(
            status="success",
            data=read_blog_data(request.blog_id),
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc