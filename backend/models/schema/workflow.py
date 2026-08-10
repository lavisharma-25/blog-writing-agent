from pydantic import BaseModel, Field
from typing import Any, Literal, Optional


class WorkflowRequest(BaseModel):
    """Request payload for executing the workflow."""

    topic: str = Field(..., min_length=1)
    audience: Optional[str] = None
    tone: Optional[str] = None
    blog_kind: Optional[Literal["explainer", "tutorial", "news_roundup", "comparison", "system_design"]] = None
    word_count: Optional[int] = Field(default=None, gt=0)
    research_mode: Optional[Literal["auto", "force", "none"]] = "auto"
    include_images: bool = False
    output_format: Literal["md", "html", "pdf", "docx"] = "md"


class WorkflowResponse(BaseModel):
    """Response returned after successful workflow execution."""

    status: Literal["success", "error"]
    data: dict[str, Any]