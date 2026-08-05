from fastapi import HTTPException

from backend.src.core.settings import settings
from backend.src.utils.metadata_utils import read_metadata

from backend.src.models.schema import BlogResponse


async def read_blog(blog_id: str) -> BlogResponse:

    blog_metadata = await read_metadata(blog_id)

    blog_filename = blog_metadata.get("filename")
    blog_path = settings.OUTPUT_DIR / blog_filename

    if not blog_path.exists():
            raise HTTPException(status_code=404, detail="Blog file not found.")

    blog_data = blog_path.read_text(encoding="utf-8")

    return BlogResponse(
            success=True,
            data={
                "blog_id": blog_metadata.get("blog_id"),
                "filename": blog_metadata.get("filename"),
                "title": blog_metadata.get("title"),
                "markdown": blog_data
            },
        )