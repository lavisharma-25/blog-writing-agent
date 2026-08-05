from fastapi import HTTPException

from backend.src.core.settings import settings
from backend.src.utils.metadata_utils import read_metadata

from backend.src.models.schemas.delete_schema import DeleteBlogResponse


async def delete_blog(blog_id: str) -> DeleteBlogResponse:
    metadata_path = settings.OUTPUT_DIR / f"{blog_id}.json"
    blog_metadata = await read_metadata(blog_id)
    
    blog_path = settings.OUTPUT_DIR / blog_metadata.get("filename")
    
    if not blog_path.exists():
        raise HTTPException(status_code=404, detail="Blog not found.")
    blog_path.unlink()

    if metadata_path.exists():
        metadata_path.unlink()

    return DeleteBlogResponse(
        success=True,
        data={
            "filename": blog_path.name,
            "metadata": str(metadata_path)
        }     
    )