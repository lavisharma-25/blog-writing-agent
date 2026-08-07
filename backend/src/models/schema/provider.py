from typing import Any
from pydantic import BaseModel


class ProvidersResponse(BaseModel):
    """Available provider/model configuration response."""

    success: bool
    data: dict[str, Any]