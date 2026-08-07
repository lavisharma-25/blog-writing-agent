from typing import List, Literal
from pydantic import BaseModel


class LogsRequest(BaseModel):
    """Request payload for retrieving log files or log content."""
    
    value: str = ""


class LogsResponse(BaseModel):
    status: Literal["success"]
    files: List[str]
    content: List[str]