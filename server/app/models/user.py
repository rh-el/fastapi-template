from typing import Optional
import uuid
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    bio: Optional[str] = None


class UserCreate(UserBase):
    plain_password: str


class UserCreateHashed(UserBase):
    hashed_password: str


class UserLogin(SQLModel):
    email: str
    plain_password: str


class UserUpdate(SQLModel):
    username: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(SQLModel):
    email: str
    username: str
    bio: Optional[str] = None


class UserResponseWithId(UserResponse):
    id: uuid.UUID


class UserHashedPasswordResponse(SQLModel):
    email: str
    username: str
    hashed_password: str


class UserAuthResponse(UserResponse):
    access_token: str
    token_type: str
