from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field

# -----------------------------
# Blog Planning Schemas
# -----------------------------
class Task(BaseModel):
    """Represents a single section/task in the blog writing plan."""

    id: int
    title: str

    goal: str = Field(..., description="One sentence describing what the reader should be able to do/understand after this section.")
    bullets: List[str] = Field(...,
        min_length=3,
        max_length=6,
        description="3-6 concrete, non-overlapping subpoints to cover in this section.",
    )
    target_words: int = Field(..., description="Target word count for this section (120-550).")

    tags: List[str] = Field(default_factory=list)
    requires_research: bool = False
    requires_citations: bool = False
    requires_code: bool = False


class Plan(BaseModel):
    """Complete blog generation plan."""

    blog_title: str
    audience: str
    tone: str

    blog_kind: Literal["explainer", "tutorial", "news_roundup", "comparison", "system_design"] = "explainer"
    constraints: List[str] = Field(default_factory=list)

    tasks: List[Task]

# -----------------------------
# Research Schemas
# -----------------------------
class EvidenceItem(BaseModel):
    """Represents a single research source."""

    title: str
    url: str
    published_at: Optional[str] = None  # keep if Tavily provides; DO NOT rely on it
    snippet: Optional[str] = None
    source: Optional[str] = None


class EvidencePack(BaseModel):
    """Collection of evidence gathered during research."""

    evidence: List[EvidenceItem] = Field(default_factory=list)


# -----------------------------
# Routing Schemas
# -----------------------------
class RouterDecision(BaseModel):
    """Decision returned by the routing node."""

    needs_research: bool
    mode: Literal["closed_book", "hybrid", "open_book"]
    queries: List[str] = Field(default_factory=list)


# -----------------------------
# API Request & Response Schemas
# -----------------------------
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

    success: bool
    data: dict


# class BlogSummary(BaseModel):
#     """Summary for a generated blog file."""

#     blog_id: str
#     title: str
#     filename: str
#     created_at: str | None = None
#     metadata: dict[str, Any] = Field(default_factory=dict)


class BlogResponse(BaseModel):
    """Single blog response."""

    success: bool
    data: dict[str, Any]


class BlogListResponse(BaseModel):
    """Generated blog listing response."""

    success: bool
    blogs: List[dict[str, Any]]


# class ExportBlogRequest(BaseModel):
#     """Request payload for exporting a blog."""

#     output_format: Literal["md", "html", "pdf", "docx"] = "md"


class ProvidersResponse(BaseModel):
    """Available provider/model configuration response."""

    success: bool
    data: dict[str, Any]


class GetLogsRequest(BaseModel):
    """Request payload for retrieving log files or log content."""
    
    value: str = ""