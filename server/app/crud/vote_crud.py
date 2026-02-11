from typing import List, Optional
import uuid

from sqlmodel import Session, select

from app.models import Vote


def get_all_votes(session: Session) -> List[Vote]:
    query = select(Vote)
    return list(session.exec(query).all())


def get_vote(vote_id: uuid.UUID, session: Session) -> Optional[Vote]:
    query = select(Vote).where(Vote.id == vote_id)
    return session.exec(query).first()


def get_user_votes(user_id: uuid.UUID, session: Session) -> List[Vote]:
    query = select(Vote).where(Vote.user_id == user_id)
    return list(session.exec(query).all())


def create_vote(vote: Vote, session: Session) -> Vote:
    session.add(vote)
    session.commit()
    session.refresh(vote)
    return vote


def update_vote(vote: Vote, session: Session) -> Vote:
    session.add(vote)
    session.commit()
    session.refresh(vote)
    return vote


def delete_vote(vote: Vote, session: Session) -> bool:
    session.delete(vote)
    session.commit()
    return True
