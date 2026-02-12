from datetime import datetime
from typing import Optional
import uuid

from sqlmodel import Session, select
from app.models import CTVSession, Interaction
from app.models.ctv_session import SessionStatus


def create_ctv_session(
    campaign_id: uuid.UUID,
    pairing_code: str,
    expires_at: datetime,
    session: Session,
) -> CTVSession:
    ctv_session = CTVSession(
        campaign_id=campaign_id,
        pairing_code=pairing_code,
        status=SessionStatus.waiting_for_pair,
        expires_at=expires_at,
    )
    session.add(ctv_session)
    session.commit()
    session.refresh(ctv_session)
    return ctv_session


def get_ctv_session_by_id(session_id: uuid.UUID, db: Session) -> Optional[CTVSession]:
    return db.exec(select(CTVSession).where(CTVSession.id == session_id)).first()


def get_active_session_by_pairing_code(
    campaign_id: uuid.UUID,
    pairing_code: str,
    db: Session,
) -> Optional[CTVSession]:
    return db.exec(
        select(CTVSession).where(
            CTVSession.campaign_id == campaign_id,
            CTVSession.pairing_code == pairing_code,
            CTVSession.status == SessionStatus.waiting_for_pair,
        )
    ).first()


def get_active_pairing_codes_for_campaign(
    campaign_id: uuid.UUID,
    db: Session,
) -> list[str]:
    results = db.exec(
        select(CTVSession.pairing_code).where(
            CTVSession.campaign_id == campaign_id,
            CTVSession.status.in_([SessionStatus.waiting_for_pair, SessionStatus.paired]),  # type: ignore[union-attr]
        )
    ).all()
    return list(results)


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
