from datetime import datetime
from typing import Optional
import uuid

from sqlmodel import Session, select
from app.models import CTVSession, Interaction
from app.models.ctv_session import SessionStatus


def create_ctv_session(
    campaign_id: uuid.UUID,
    claim_token_hash: str,
    claim_token_expires_at: datetime,
    expires_at: datetime,
    session: Session,
) -> CTVSession:
    ctv_session = CTVSession(
        campaign_id=campaign_id,
        pairing_code=None,
        claim_token_hash=claim_token_hash,
        claim_token_expires_at=claim_token_expires_at,
        status=SessionStatus.waiting_for_pair,
        expires_at=expires_at,
    )
    session.add(ctv_session)
    session.commit()
    session.refresh(ctv_session)
    return ctv_session


def get_ctv_session_by_id(session_id: uuid.UUID, db: Session) -> Optional[CTVSession]:
    return db.exec(select(CTVSession).where(CTVSession.id == session_id)).first()

def get_session_by_claim_token_hash(
    claim_token_hash: str,
    db: Session,
) -> Optional[CTVSession]:
    return db.exec(select(CTVSession).where(CTVSession.claim_token_hash == claim_token_hash)).first()


def update_session_status(
    ctv_session: CTVSession,
    status: SessionStatus,
    db: Session,
) -> CTVSession:
    ctv_session.status = status
    if status == SessionStatus.paired:
        ctv_session.paired_at = datetime.now()
    db.add(ctv_session)
    db.commit()
    db.refresh(ctv_session)
    return ctv_session


def create_interaction(
    session_id: uuid.UUID,
    action_type: str,
    payload: dict,
    db: Session,
) -> Interaction:
    interaction = Interaction(
        session_id=session_id,
        action_type=action_type,
        payload=payload,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction
