from datetime import datetime
from typing import List, Optional
import uuid

from sqlmodel import Field, Relationship
from app.models.user import UserBase
from app.models.vote import VoteBase


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.now})

    votes: List["Vote"] = Relationship(back_populates="user")


class Vote(VoteBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.now})

    user_id: uuid.UUID = Field(foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="votes")


__all__ = ["User", "Vote"]
