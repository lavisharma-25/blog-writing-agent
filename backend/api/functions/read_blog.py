from fastapi import HTTPException

from backend.core.settings import settings
from backend.utils.metadata_utils import read_metadata
from backend.models.schema.read import ReadBlogRequest, ReadBlogResponse


def read_blog(request: ReadBlogRequest) -> ReadBlogResponse:

    blog_metadata = read_metadata(request.blog_id)

    blog_filename = blog_metadata.get("filename")
    blog_path = settings.OUTPUT_DIR / blog_filename

    if not blog_path.exists():
            raise HTTPException(status_code=404, detail="Blog file not found.")

    blog_data = blog_path.read_text(encoding="utf-8")

    return ReadBlogResponse(
            status="success",
            data={
                "blog_id": blog_metadata.get("blog_id"),
                "filename": blog_metadata.get("filename"),
                "title": blog_metadata.get("title"),
                "markdown": blog_data
            },
        )