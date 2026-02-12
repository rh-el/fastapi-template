from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid
from sqlmodel import Field, SQLModel


class SessionStatus(str, Enum):
    waiting_for_pair = "waiting_for_pair"
    paired = "paired"
    expired = "expired"
    closed = "closed"


class CTVSessionBase(SQLModel):
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    pairing_code: str = Field(index=True)
    status: SessionStatus = Field(default=SessionStatus.waiting_for_pair)


class CTVSessionRegister(SQLModel):
    campaign_id: uuid.UUID


class CTVSessionPair(SQLModel):
    campaign_id: uuid.UUID
    pairing_code: str


class CTVSessionResponse(SQLModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    pairing_code: str
    status: SessionStatus
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class CTVSessionPairResponse(SQLModel):
    session_id: uuid.UUID
    interaction_config: list[dict[str, Any]] = []
