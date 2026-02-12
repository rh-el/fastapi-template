import uuid
from fastapi import APIRouter, Depends

from app.core.dependencies import get_session_service
from app.models.ctv_session import (
    CTVSessionPair,
    CTVSessionPairResponse,
    CTVSessionRegister,
    CTVSessionResponse,
)
from app.models.interaction import InteractionCreate, InteractionResponse
from app.services.session_service import SessionService

router = APIRouter(prefix="/session", tags=["sessions"])


@router.post("/register", response_model=CTVSessionResponse, status_code=201)
def register_session(
    data: CTVSessionRegister,
    session_service: SessionService = Depends(get_session_service),
):
    """Called by CTV ad creative after the viewer presses a button on the remote."""
    return session_service.register_session(data.campaign_id)


@router.post("/pair", response_model=CTVSessionPairResponse, status_code=200)
async def pair_session(
    data: CTVSessionPair,
    session_service: SessionService = Depends(get_session_service),
):
    """Called by the smartphone after scanning the QR code and entering the pairing code."""
    return await session_service.pair_session(data.campaign_id, data.pairing_code)


@router.post("/{session_id}/interact", response_model=InteractionResponse, status_code=201)
async def interact(
    session_id: uuid.UUID,
    data: InteractionCreate,
    session_service: SessionService = Depends(get_session_service),
):
    """Called by the smartphone when the user taps an action button."""
    return await session_service.handle_interaction(session_id, data)


@router.get("/{session_id}", response_model=CTVSessionResponse, status_code=200)
def get_session_status(
    session_id: uuid.UUID,
    session_service: SessionService = Depends(get_session_service),
):
    """Get current session status (useful for polling fallback)."""
    return session_service.get_session_status(session_id)
