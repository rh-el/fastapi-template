from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
import uuid

import jwt
from sqlmodel import Session
from app.core.config import settings
from app.core.exceptions import (
    CampaignNotFoundException,
    ClaimTokenExpiredException,
    InteractionTokenInvalidException,
    InvalidClaimTokenException,
    PairingDisabledException,
    SessionAlreadyPairedException,
    SessionExpiredException,
    SessionNotFoundException,
    SessionNotPairedException,
)
from app.crud.campaign_crud import get_campaign_by_id
from app.crud.session_crud import (
    create_ctv_session,
    create_interaction,
    get_ctv_session_by_id,
    get_session_by_claim_token_hash,
    update_session_status,
)
from app.models import CTVSession
from app.models.ctv_session import (
    CTVSessionClaimResponse,
    CTVSessionRegisterResponse,
    CTVSessionStatusResponse,
    SessionStatus,
)
from app.models.interaction import InteractionCreate, InteractionResponse

SESSION_EXPIRY_SECONDS = 120
INTERACTION_TOKEN_GRACE_SECONDS = 2


class SessionService:
    def __init__(self, session: Session):
        self.session = session

    def _hash_claim_token(self, claim_token: str) -> str:
        if not settings.JWT_SECRET_KEY:
            raise RuntimeError("JWT_SECRET_KEY is not configured")
        digest = hmac.new(
            settings.JWT_SECRET_KEY.encode("utf-8"),
            claim_token.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return digest

    def _create_interaction_token(self, session_id: uuid.UUID, expires_at: datetime) -> str:
        if not settings.JWT_SECRET_KEY:
            raise RuntimeError("JWT_SECRET_KEY is not configured")
        now = datetime.now()
        payload = {
            "typ": "ctv_session_interaction",
            "sid": str(session_id),
            "iat": now,
            "exp": expires_at,
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def _verify_interaction_token(self, token: str, session_id: uuid.UUID) -> None:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"require": ["exp", "iat"]},
            )
        except jwt.InvalidTokenError:
            raise InteractionTokenInvalidException()

        if payload.get("typ") != "ctv_session_interaction":
            raise InteractionTokenInvalidException()
        if payload.get("sid") != str(session_id):
            raise InteractionTokenInvalidException()

    def _check_session_expiry(self, ctv_session: CTVSession) -> None:
        if ctv_session.expires_at and datetime.now() > ctv_session.expires_at:
            if ctv_session.status not in (SessionStatus.expired, SessionStatus.closed):
                update_session_status(ctv_session, SessionStatus.expired, self.session)
            raise SessionExpiredException(ctv_session.id)

    def register_session(self, campaign_id: uuid.UUID) -> CTVSessionRegisterResponse:
        campaign = get_campaign_by_id(campaign_id, self.session)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)

        claim_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=SESSION_EXPIRY_SECONDS)
        claim_token_expires_at = expires_at

        ctv_session = create_ctv_session(
            campaign_id=campaign_id,
            claim_token_hash=self._hash_claim_token(claim_token),
            claim_token_expires_at=claim_token_expires_at,
            expires_at=expires_at,
            session=self.session,
        )

        qr_url = f"{campaign.qr_base_url}#claim={claim_token}"

        return CTVSessionRegisterResponse(
            id=ctv_session.id,
            campaign_id=ctv_session.campaign_id,
            status=ctv_session.status,
            claim_token=claim_token,
            qr_url=qr_url,
            created_at=ctv_session.created_at,
            expires_at=ctv_session.expires_at,
        )

    async def pair_session(self, *_args, **_kwargs):
        raise PairingDisabledException()

    async def claim_session(
        self,
        claim_token: str,
        campaign_id: uuid.UUID | None = None,
    ) -> CTVSessionClaimResponse:
        ctv_session = get_session_by_claim_token_hash(self._hash_claim_token(claim_token), self.session)
        if not ctv_session:
            raise InvalidClaimTokenException()

        if campaign_id and ctv_session.campaign_id != campaign_id:
            raise InvalidClaimTokenException()

        if ctv_session.claim_token_expires_at and datetime.now() > ctv_session.claim_token_expires_at:
            raise ClaimTokenExpiredException()

        self._check_session_expiry(ctv_session)

        if ctv_session.status == SessionStatus.paired:
            raise SessionAlreadyPairedException(ctv_session.id)

        campaign = get_campaign_by_id(ctv_session.campaign_id, self.session)
        if not campaign:
            raise CampaignNotFoundException(ctv_session.campaign_id)

        updated = update_session_status(ctv_session, SessionStatus.paired, self.session)

        exp = updated.expires_at or (datetime.now() + timedelta(seconds=SESSION_EXPIRY_SECONDS))
        exp = exp + timedelta(seconds=INTERACTION_TOKEN_GRACE_SECONDS)
        interaction_token = self._create_interaction_token(updated.id, exp)

        return CTVSessionClaimResponse(
            session_id=updated.id,
            interaction_config=campaign.interaction_config or [],
            interaction_token=interaction_token,
            expires_at=updated.expires_at,
        )

    async def handle_interaction(
        self,
        session_id: uuid.UUID,
        interaction_data: InteractionCreate,
        interaction_token: str,
    ) -> InteractionResponse:
        self._verify_interaction_token(interaction_token, session_id)

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

        return InteractionResponse(
            id=interaction.id,
            session_id=interaction.session_id,
            action_type=interaction.action_type,
            payload=interaction.payload or {},
            created_at=interaction.created_at,
        )

    def get_session_status(self, session_id: uuid.UUID) -> CTVSessionStatusResponse:
        ctv_session = get_ctv_session_by_id(session_id, self.session)
        if not ctv_session:
            raise SessionNotFoundException(session_id)

        if ctv_session.expires_at and datetime.now() > ctv_session.expires_at:
            if ctv_session.status not in (SessionStatus.expired, SessionStatus.closed):
                update_session_status(ctv_session, SessionStatus.expired, self.session)
                ctv_session.status = SessionStatus.expired

        return CTVSessionStatusResponse(
            id=ctv_session.id,
            campaign_id=ctv_session.campaign_id,
            status=ctv_session.status,
            created_at=ctv_session.created_at,
            expires_at=ctv_session.expires_at,
        )
