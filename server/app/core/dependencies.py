from typing import Annotated, Optional
from fastapi import Depends, HTTPException, Request, status
import jwt
from sqlmodel import Session

from app.core.exceptions import UserTokenInvalidException
from app.crud.user_crud import get_user_by_email
from app.db import get_session
from app.models.token import TokenData
from app.models.user import UserResponseWithId
from app.services.user_service import UserService
from app.services.vote_service import VoteService
from app.services.campaign_service import CampaignService
from app.services.session_service import SessionService
from app.core.config import settings
from app.core.security import oauth2_scheme

COOKIE_NAME = "access_token"


def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(session)


def get_vote_service(session: Session = Depends(get_session)) -> VoteService:
    return VoteService(session)


def get_campaign_service(session: Session = Depends(get_session)) -> CampaignService:
    return CampaignService(session)


def get_session_service(session: Session = Depends(get_session)) -> SessionService:
    return SessionService(session)


def get_token(request: Request, header_token: Optional[str] = Depends(oauth2_scheme)) -> str:
    cookie_token = request.cookies.get(COOKIE_NAME)
    if cookie_token:
        return cookie_token
    if header_token:
        return header_token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Annotated[str, Depends(get_token)],
    user_service: UserService = Depends(get_user_service),
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise UserTokenInvalidException()
        token_data = TokenData(email=email)
        if token_data.email is None:
            raise UserTokenInvalidException()
        user = get_user_by_email(token_data.email, user_service.session)
        if user is None:
            raise UserTokenInvalidException()
        return user
    except jwt.InvalidTokenError:
        raise UserTokenInvalidException()


def get_current_active_user(
    current_user: UserResponseWithId = Depends(get_current_user),
):
    return current_user
