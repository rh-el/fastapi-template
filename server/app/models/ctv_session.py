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
    pairing_code: Optional[str] = Field(default=None, index=True)
    claim_token_hash: Optional[str] = Field(default=None, index=True)
    claim_token_expires_at: Optional[datetime] = Field(default=None)
    status: SessionStatus = Field(default=SessionStatus.waiting_for_pair)


class CTVSessionRegister(SQLModel):
    campaign_id: uuid.UUID


class CTVSessionClaim(SQLModel):
    claim_token: str
    campaign_id: Optional[uuid.UUID] = None


class CTVSessionRegisterResponse(SQLModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    status: SessionStatus
    claim_token: str
    qr_url: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class CTVSessionStatusResponse(SQLModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    status: SessionStatus
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class CTVSessionClaimResponse(SQLModel):
    session_id: uuid.UUID
    interaction_config: list[dict[str, Any]] = []
    interaction_token: str
    expires_at: Optional[datetime] = None
