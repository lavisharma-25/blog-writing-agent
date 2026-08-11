from fastapi import HTTPException

from backend.services.blog_service import delete_blog_data
from backend.models.schema.delete import DeleteBlogRequest, DeleteBlogResponse


def delete_blog(request: DeleteBlogRequest) -> DeleteBlogResponse:
    try:
        return DeleteBlogResponse(
            status="success",
            data=delete_blog_data(request.blog_id),
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc