from backend.models.schema.list import BlogListResponse
from backend.services.blog_service import list_blog_data


def list_blogs() -> BlogListResponse:
    return BlogListResponse(
        status="success",
        data=list_blog_data(),
    )