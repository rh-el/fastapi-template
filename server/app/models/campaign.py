from datetime import datetime
from typing import Any, Optional
import uuid
from sqlmodel import Field, SQLModel


class CampaignBase(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    qr_base_url: str
    is_active: bool = Field(default=True)


class CampaignCreate(SQLModel):
    name: str
    description: Optional[str] = None
    interaction_config: list[dict[str, Any]] = []
    qr_base_url: str


class CampaignResponse(SQLModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    interaction_config: list[dict[str, Any]] = []
    qr_base_url: str
    is_active: bool
    created_at: Optional[datetime] = None
