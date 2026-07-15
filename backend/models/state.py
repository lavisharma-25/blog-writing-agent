import operator
from typing import Annotated
from pydantic import BaseModel, Field

from backend.models.schema import Plan


class State(BaseModel):
    topic: str
    plan: Plan | None = None
    sections: Annotated[list[str], operator.add] = Field(default_factory=list)
    final: str = ""
