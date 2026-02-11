from typing import Optional

from sqlmodel import Session, select
from app.models import User
from app.models.user import (
    UserCreateHashed,
    UserHashedPasswordResponse,
    UserResponse,
    UserResponseWithId,
    UserUpdate,
)


def get_user_by_email(email: str, session: Session) -> Optional[UserResponseWithId]:
    query = select(User).where(User.email == email)
    db_user = session.exec(query).first()
    if not db_user:
        return None
    assert db_user.id
    return UserResponseWithId(
        email=db_user.email,
        username=db_user.username,
        bio=db_user.bio,
        id=db_user.id,
    )


def get_user_by_username(username: str, session: Session) -> Optional[UserResponse]:
    query = select(User).where(User.username == username)
    db_user = session.exec(query).first()
    if not db_user:
        return None
    return UserResponse(
        email=db_user.email,
        username=db_user.username,
        bio=db_user.bio,
    )


def create_user(user: UserCreateHashed, session: Session):
    new_user = User(
        email=user.email,
        username=user.username,
        bio=user.bio,
        hashed_password=user.hashed_password,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def get_user_hashed_password(email: str, session: Session):
    query = select(User).where(User.email == email)
    db_user = session.exec(query).first()
    if not db_user:
        return None
    return UserHashedPasswordResponse(
        email=db_user.email,
        username=db_user.username,
        hashed_password=db_user.hashed_password,
    )


def update_user(user_data: UserUpdate, email: str, session: Session):
    db_user = session.exec(select(User).where(User.email == email)).first()
    if not db_user:
        return None

    for key, value in user_data.model_dump(exclude_none=True).items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(email: str, session: Session) -> bool:
    db_user = session.exec(select(User).where(User.email == email)).first()
    if not db_user:
        return False
    session.delete(db_user)
    return True
