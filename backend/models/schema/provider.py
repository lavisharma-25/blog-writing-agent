from typing import Literal
from pydantic import BaseModel


class ProviderInfo(BaseModel):
    model: str | None = None
    base_url: str | None = None
    location: str | None = None


class CustomOpenAISlot(BaseModel):
    model: str | None
    base_url: str | None


class ProvidersData(BaseModel):
    active_provider: str
    custom_provider: str | None
    providers: dict[str, ProviderInfo]
    custom_openai_slot: CustomOpenAISlot


class ProvidersResponse(BaseModel):
    """Available provider/model configuration response."""

    status: Literal["success", "error"]
    data: ProvidersData