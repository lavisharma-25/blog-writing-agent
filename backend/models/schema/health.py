from typing import Literal
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response payload for health check."""

    status: Literal["success", "error"]
    message: str