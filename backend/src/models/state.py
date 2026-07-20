import operator
from typing import List, Optional, Annotated
from pydantic import BaseModel, Field

from backend.src.models.schema import Plan, EvidenceItem


class State(BaseModel):
    topic: str

    # routing / research
    mode: str
    needs_research: bool
    queries: List[str]
    evidence: List[EvidenceItem]
    plan: Optional[Plan]

    # writer
    sections: Annotated[list[tuple[int, str]], operator.add] = Field(default_factory=list) # (task_id, section_md)
    final: str = ""
