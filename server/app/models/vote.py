from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class VoteBase(SQLModel):
    title: str
    description: Optional[str] = None


class VoteCreate(VoteBase):
    pass  # user_id is injected from auth


class VoteUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None


class VoteResponse(VoteBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: Optional[datetime] = None
