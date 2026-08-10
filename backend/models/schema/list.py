from typing import Any, List, Literal
from pydantic import BaseModel


class BlogListResponse(BaseModel):
    """Generated blog listing response."""

    status: Literal["success", "error"]
    blogs: List[dict[str, Any]]