from datetime import datetime
from typing import Any, Optional
import uuid
from sqlmodel import Field, SQLModel


class InteractionBase(SQLModel):
    session_id: uuid.UUID = Field(foreign_key="ctvsession.id")
    action_type: str


class InteractionCreate(SQLModel):
    action_type: str
    payload: dict[str, Any] = {}


class InteractionResponse(SQLModel):
    id: uuid.UUID
    session_id: uuid.UUID
    action_type: str
    payload: dict[str, Any] = {}
    created_at: Optional[datetime] = None
