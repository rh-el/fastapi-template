import random
import string
from datetime import datetime, timedelta
import uuid

from sqlmodel import Session
from app.core.exceptions import (
    CampaignNotFoundException,
    InvalidPairingCodeException,
    SessionAlreadyPairedException,
    SessionExpiredException,
    SessionNotFoundException,
    SessionNotPairedException,
)
from app.core.ws_manager import ws_manager
from app.crud.campaign_crud import get_campaign_by_id
from app.crud.session_crud import (
    create_ctv_session,
    create_interaction,
    get_active_session_by_pairing_code,
    get_active_pairing_codes_for_campaign,
    get_ctv_session_by_id,
    update_session_status,
)
from app.models.ctv_session import (
    CTVSessionPairResponse,
    CTVSessionResponse,
    SessionStatus,
)
from app.models.interaction import InteractionCreate, InteractionResponse

PAIRING_CODE_LENGTH = 4
SESSION_EXPIRY_UNPAIRED_MINUTES = 5
SESSION_EXPIRY_PAIRED_MINUTES = 30


class SessionService:
    def __init__(self, session: Session):
        self.session = session

    def _generate_pairing_code(self, campaign_id: uuid.UUID) -> str:
        """Generate a unique 4-char alphanumeric pairing code for this campaign."""
        existing = get_active_pairing_codes_for_campaign(campaign_id, self.session)
        existing_upper = {code.upper() for code in existing}

        chars = string.ascii_uppercase + string.digits
        for _ in range(100):  # max attempts
            code = "".join(random.choices(chars, k=PAIRING_CODE_LENGTH))
            if code not in existing_upper:
                return code
        raise RuntimeError("Could not generate unique pairing code after 100 attempts")

    def _check_session_expiry(self, ctv_session) -> None:
        """Raise SessionExpiredException if the session has expired, updating status if needed."""
        if ctv_session.expires_at and datetime.now() > ctv_session.expires_at:
            if ctv_session.status not in (SessionStatus.expired, SessionStatus.closed):
                update_session_status(ctv_session, SessionStatus.expired, self.session)
            raise SessionExpiredException(ctv_session.id)

    def register_session(self, campaign_id: uuid.UUID) -> CTVSessionResponse:
        """Called by CTV ad creative after viewer presses remote button."""
        campaign = get_campaign_by_id(campaign_id, self.session)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)

        pairing_code = self._generate_pairing_code(campaign_id)
        expires_at = datetime.now() + timedelta(minutes=SESSION_EXPIRY_UNPAIRED_MINUTES)

        ctv_session = create_ctv_session(campaign_id, pairing_code, expires_at, self.session)
        return CTVSessionResponse(
            id=ctv_session.id,
            campaign_id=ctv_session.campaign_id,
            pairing_code=ctv_session.pairing_code,
            status=ctv_session.status,
            created_at=ctv_session.created_at,
            expires_at=ctv_session.expires_at,
        )

    async def pair_session(self, campaign_id: uuid.UUID, pairing_code: str) -> CTVSessionPairResponse:
        """Called by smartphone after user enters pairing code."""
        campaign = get_campaign_by_id(campaign_id, self.session)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)

        ctv_session = get_active_session_by_pairing_code(
            campaign_id, pairing_code.upper(), self.session
        )
        if not ctv_session:
            raise InvalidPairingCodeException()

        self._check_session_expiry(ctv_session)

        if ctv_session.status == SessionStatus.paired:
            raise SessionAlreadyPairedException(ctv_session.id)

        # Extend expiry on pairing
        ctv_session.expires_at = datetime.now() + timedelta(minutes=SESSION_EXPIRY_PAIRED_MINUTES)
        updated = update_session_status(ctv_session, SessionStatus.paired, self.session)

        # Notify CTV via WebSocket that a phone has paired
        await ws_manager.send_to_session(
            str(updated.id),
            {"event": "session_paired", "data": {}},
        )

        return CTVSessionPairResponse(
            session_id=updated.id,
            interaction_config=campaign.interaction_config or [],
        )

    async def handle_interaction(
        self,
        session_id: uuid.UUID,
        interaction_data: InteractionCreate,
    ) -> InteractionResponse:
        """Called by smartphone when user taps an action button."""
        ctv_session = get_ctv_session_by_id(session_id, self.session)
        if not ctv_session:
            raise SessionNotFoundException(session_id)

        self._check_session_expiry(ctv_session)

        if ctv_session.status != SessionStatus.paired:
            raise SessionNotPairedException(session_id)

        interaction = create_interaction(
            session_id=session_id,
            action_type=interaction_data.action_type,
            payload=interaction_data.payload,
            db=self.session,
        )

        # Push lightweight event to CTV via WebSocket
        await ws_manager.send_to_session(
            str(session_id),
            {
                "event": "interaction",
                "data": {
                    "action_type": interaction_data.action_type,
                    "payload": interaction_data.payload,
                },
            },
        )

        return InteractionResponse(
            id=interaction.id,
            session_id=interaction.session_id,
            action_type=interaction.action_type,
            payload=interaction.payload or {},
            created_at=interaction.created_at,
        )

    def get_session_status(self, session_id: uuid.UUID) -> CTVSessionResponse:
        """Get current session status (useful for polling fallback)."""
        ctv_session = get_ctv_session_by_id(session_id, self.session)
        if not ctv_session:
            raise SessionNotFoundException(session_id)

        # Check expiry silently and update status if needed
        if ctv_session.expires_at and datetime.now() > ctv_session.expires_at:
            if ctv_session.status not in (SessionStatus.expired, SessionStatus.closed):
                update_session_status(ctv_session, SessionStatus.expired, self.session)
                ctv_session.status = SessionStatus.expired

        return CTVSessionResponse(
            id=ctv_session.id,
            campaign_id=ctv_session.campaign_id,
            pairing_code=ctv_session.pairing_code,
            status=ctv_session.status,
            created_at=ctv_session.created_at,
            expires_at=ctv_session.expires_at,
        )
