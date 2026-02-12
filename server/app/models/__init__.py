from datetime import datetime
from typing import Any, List, Optional
import uuid

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship
from app.models.user import UserBase
from app.models.vote import VoteBase
from app.models.campaign import CampaignBase
from app.models.ctv_session import CTVSessionBase
from app.models.interaction import InteractionBase


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.now})


class Vote(VoteBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.now})


class Campaign(CampaignBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    interaction_config: Optional[list] = Field(default=[], sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.now})


class CTVSession(CTVSessionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    paired_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=None)


class Interaction(InteractionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    payload: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default_factory=datetime.now)


__all__ = ["User", "Vote", "Campaign", "CTVSession", "Interaction"]
