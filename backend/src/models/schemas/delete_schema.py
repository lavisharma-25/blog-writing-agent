from typing import Any
from pydantic import BaseModel


class DeleteBlogResponse(BaseModel):
    """Response payload for deleting a blog."""
    
    success: bool
    data: dict[str, Any]