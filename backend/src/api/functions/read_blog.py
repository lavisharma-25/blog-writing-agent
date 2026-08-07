from fastapi import HTTPException

from backend.src.models import schema
from backend.src.core.settings import settings
from backend.src.utils.metadata_utils import read_metadata


async def read_blog(request: schema.ReadBlogRequest) -> schema.ReadBlogResponse:

    blog_metadata = await read_metadata(request.blog_id)

    blog_filename = blog_metadata.get("filename")
    blog_path = settings.OUTPUT_DIR / blog_filename

    if not blog_path.exists():
            raise HTTPException(status_code=404, detail="Blog file not found.")

    blog_data = blog_path.read_text(encoding="utf-8")

    return schema.ReadBlogResponse(
            status="success",
            data={
                "blog_id": blog_metadata.get("blog_id"),
                "filename": blog_metadata.get("filename"),
                "title": blog_metadata.get("title"),
                "markdown": blog_data
            },
        )