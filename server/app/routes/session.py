import uuid
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.dependencies import get_session_service
from app.models.ctv_session import (
    CTVSessionClaim,
    CTVSessionClaimResponse,
    CTVSessionRegister,
    CTVSessionRegisterResponse,
    CTVSessionStatusResponse,
)
from app.models.interaction import InteractionCreate, InteractionResponse
from app.services.session_service import SessionService

router = APIRouter(prefix="/session", tags=["sessions"])
interaction_bearer = HTTPBearer(auto_error=False)


@router.post("/register", response_model=CTVSessionRegisterResponse, status_code=201)
def register_session(
    data: CTVSessionRegister,
    session_service: SessionService = Depends(get_session_service),
):
    """called by the ctv after pressing a button"""
    return session_service.register_session(data.campaign_id)


@router.post("/claim", response_model=CTVSessionClaimResponse, status_code=200)
async def claim_session(
    data: CTVSessionClaim,
    session_service: SessionService = Depends(get_session_service),
):
    """called by the smartphone after qrcode scan"""
    return await session_service.claim_session(data.claim_token, data.campaign_id)


@router.post("/interact/{session_id}", response_model=InteractionResponse, status_code=201)
async def interact(
    session_id: uuid.UUID,
    data: InteractionCreate,
    creds: HTTPAuthorizationCredentials | None = Depends(interaction_bearer),
    session_service: SessionService = Depends(get_session_service),
):
    """called on each smartphone interaction"""
    token = creds.credentials if creds else ""
    return await session_service.handle_interaction(session_id, data, token)


@router.get("/{session_id}", response_model=CTVSessionStatusResponse, status_code=200)
def get_session_status(
    session_id: uuid.UUID,
    session_service: SessionService = Depends(get_session_service),
):
    return session_service.get_session_status(session_id)
