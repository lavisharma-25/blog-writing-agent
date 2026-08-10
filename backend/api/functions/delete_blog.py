from fastapi import HTTPException

from backend.core.settings import settings
from backend.utils.metadata_utils import read_metadata

from backend.models import schema


async def delete_blog(request: schema.DeleteBlogRequest) -> schema.DeleteBlogResponse:
    """ Delete a blog and its associated metadata."""

    blog_id = request.blog_id
    
    metadata_path = settings.OUTPUT_DIR / f"{blog_id}.json"
    blog_metadata = await read_metadata(blog_id)
    
    blog_path = settings.OUTPUT_DIR / blog_metadata.get("filename")
    
    if not blog_path.exists():
        raise HTTPException(status_code=404, detail="Blog not found.")
    blog_path.unlink()

    if metadata_path.exists():
        metadata_path.unlink()

    return schema.DeleteBlogResponse(
        status="success",
        data={
            "filename": blog_path.name,
            "metadata": str(metadata_path)
        }     
    )