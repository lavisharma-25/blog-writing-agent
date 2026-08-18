from typing import List, Literal
from pydantic import BaseModel


class BlogListData(BaseModel):
    blog_id: str
    blog_path: str | None
    title: str | None
    user_query: str | None
    created_at: str | None


class BlogListResponse(BaseModel):
    """Generated blog listing response."""

    status: Literal["success", "error"]
    data: List[BlogListData]