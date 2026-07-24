from typing import List, Literal, Optional
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


class WorkflowResponse(BaseModel):
    """Response returned after successful workflow execution."""

    success: bool
    data: dict


class GetLogsRequest(BaseModel):
    """Request payload for retrieving log files or log content."""
    
    value: str = ""