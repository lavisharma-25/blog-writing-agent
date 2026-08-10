from typing import Any, Literal
from pydantic import BaseModel


class DeleteBlogRequest(BaseModel):
    """Request payload for deleting a blog."""

    blog_id: str


class DeleteBlogResponse(BaseModel):
    """Response payload for deleting a blog."""
    
    status: Literal["success", "error"]
    data: dict[str, Any]