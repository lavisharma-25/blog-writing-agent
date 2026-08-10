from typing import Any, Literal
from pydantic import BaseModel


class ProvidersResponse(BaseModel):
    """Available provider/model configuration response."""

    status: Literal["success", "error"]
    data: dict[str, Any]