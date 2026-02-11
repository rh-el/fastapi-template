from fastapi import APIRouter, Depends, Response, status
from app.models import User
from sqlmodel import Session, select
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from app.db import get_session
from app.models.user import UserCreate, UserResponse, UserResponseWithId, UserUpdate
from app.core.dependencies import get_current_active_user, get_user_service
from app.services.user_service import UserService
from app.core.config import settings

router = APIRouter(prefix="/user", tags=["users"])

COOKIE_NAME = "access_token"


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )


@router.post("/signup", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    response: Response,
    user_service: UserService = Depends(get_user_service),
):
    new_user = user_service.create_user(user)
    access_token = user_service.create_access_token(user.email)
    set_auth_cookie(response, access_token)
    return UserResponse(**new_user.model_dump(exclude_unset=True))


@router.post("/token", response_model=UserResponse)
def get_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(get_user_service),
):
    user = user_service.authenticate_user(form_data.username, form_data.password)
    access_token = user_service.create_access_token(user.email)
    set_auth_cookie(response, access_token)
    return UserResponse(**user.model_dump(exclude_unset=True))


@router.get("/", response_model=list[UserResponse])
def get_all_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@router.get("/me", response_model=UserResponse)
def get_user_informations(
    current_user: Annotated[UserResponseWithId, Depends(get_current_active_user)],
):
    return current_user


@router.put("/", response_model=UserResponse)
def update_user_data(
    user_update: UserUpdate,
    current_user: Annotated[UserResponseWithId, Depends(get_current_active_user)],
    user_service: UserService = Depends(get_user_service),
):
    return user_service.update_user_data(user_update, current_user)


@router.delete("/delete")
def delete_user(
    response: Response,
    current_user: Annotated[UserResponseWithId, Depends(get_current_active_user)],
    user_service: UserService = Depends(get_user_service),
):
    user_service.delete_user(current_user)
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"message": "Logged out successfully"}
