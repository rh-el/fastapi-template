from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.core.exceptions import (
    UserCredentialsException,
    UserEmailAlreadyExistsException,
    UserNotFoundException,
    UsernameAlreadyExistsException,
)
from app.core.config import settings
from app.crud.user_crud import (
    create_user,
    delete_user,
    get_user_by_email,
    get_user_by_username,
    get_user_hashed_password,
    update_user,
)

import jwt
from sqlmodel import Session
from app.models.user import UserCreate, UserCreateHashed, UserResponse, UserUpdate
from argon2 import PasswordHasher

ph = PasswordHasher()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return ph.verify(hashed_password, plain_password)


def get_password_hash(plain_password: str) -> str:
    return ph.hash(plain_password)


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.jwt_secret_key = settings.JWT_SECRET_KEY
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_days = settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS

    def create_access_token(self, email: str) -> str:
        access_token_expires = timedelta(days=self.access_token_expire_days)
        return self.generate_access_token(
            data={"sub": email},
            expires_delta=access_token_expires,
        )

    def generate_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.jwt_algorithm)

    def authenticate_user(self, email: str, password: str):
        user = get_user_hashed_password(email, self.session)
        if not user:
            raise UserNotFoundException(email)
        if not verify_password(password, user.hashed_password):
            raise UserCredentialsException()
        return user

    def create_user(self, user_data: UserCreate):
        db_user = get_user_by_email(user_data.email, self.session)
        db_user_by_username = get_user_by_username(user_data.username, self.session)

        if db_user:
            raise UserEmailAlreadyExistsException(user_data.email)
        if db_user_by_username:
            raise UsernameAlreadyExistsException(user_data.username)

        hashed_password = get_password_hash(user_data.plain_password)
        new_user = UserCreateHashed(
            email=user_data.email,
            username=user_data.username,
            bio=user_data.bio,
            hashed_password=hashed_password,
        )
        return create_user(new_user, self.session)

    def update_user_data(self, user_update: UserUpdate, current_user: UserResponse):
        if user_update.username:
            db_user = get_user_by_username(user_update.username, self.session)
            if db_user and db_user.email != current_user.email:
                raise UsernameAlreadyExistsException(user_update.username)

        return update_user(user_update, current_user.email, self.session)

    def delete_user(self, current_user: UserResponse):
        deleted = delete_user(current_user.email, self.session)
        if not deleted:
            raise UserNotFoundException(current_user.email)
        self.session.commit()
