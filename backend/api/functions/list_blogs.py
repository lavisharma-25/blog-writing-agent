from backend.core.settings import settings
from backend.utils.metadata_utils import read_metadata
from backend.models.schema.list import BlogListResponse


async def list_blogs() -> BlogListResponse:
    blogs = []
    for path in sorted(settings.OUTPUT_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):

        blog_id = path.stem

        metadata = await read_metadata(blog_id)

        blogs.append(
            {
                "blog_id": blog_id,
                "filename": metadata.get("filename"),
                "title": metadata.get("title"),
                "user_query": metadata.get("topic"),
                "created_at": metadata.get("created_at") or None
            }
        )

    return BlogListResponse(
        status="success",
        blogs=blogs
    )