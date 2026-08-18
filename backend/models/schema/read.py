from typing import Literal
from pydantic import BaseModel


class ReadBlogRequest(BaseModel):
    """Request payload for reading a blog."""
    
    blog_id: str


class ReadBlogData(BaseModel):
    """Generated blog content returned by the read endpoint."""
    blog_id: str
    blog_path: str | None
    title: str | None
    markdown: str


class ReadBlogResponse(BaseModel):
    """Response returned after reading a blog."""
    
    status: Literal["success", "error"]
    data: ReadBlogData