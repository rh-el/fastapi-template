from datetime import datetime
from enum import Enum
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel

class Role(str, Enum):
    villageois = "villageois"
    loups_garous = "loups_garous"

class VoteBase(SQLModel):
    role: Role

class VoteCreate(VoteBase):
    pass 

class VoteResponse(VoteBase):
    created_at: Optional[datetime] = None
