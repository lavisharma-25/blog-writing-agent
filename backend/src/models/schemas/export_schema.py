from typing import Literal
from pydantic import BaseModel


class ExportBlogRequest(BaseModel):
    """Request payload for exporting a blog."""

    blog_id: str
    output_format: Literal["md", "html", "pdf", "docx"] = "md"
