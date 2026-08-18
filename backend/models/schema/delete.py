from typing import Literal
from pydantic import BaseModel


class DeleteBlogRequest(BaseModel):
    """Request payload for deleting a blog."""

    blog_id: str


class DeleteBlogData(BaseModel):
    blog_id: str
    message: str


class DeleteBlogResponse(BaseModel):
    """Response payload for deleting a blog."""
    
    status: Literal["success", "error"]
    data: DeleteBlogData