from typing import Any, Literal
from pydantic import BaseModel


class ReadBlogRequest(BaseModel):
    """Request payload for reading a blog."""
    
    blog_id: str


class ReadBlogResponse(BaseModel):
    """Response returned after reading a blog."""
    
    status: Literal["success", "error"]
    data: dict[str, Any]