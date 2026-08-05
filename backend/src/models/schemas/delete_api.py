from typing import Any
from pydantic import BaseModel


class DeleteBlogResponse(BaseModel):
    success: bool
    data: dict[str, Any]