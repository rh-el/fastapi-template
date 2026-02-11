
from typing import List
from sqlmodel import Session, select
from app.models import Vote


def get_all_votes(session: Session) -> List[Vote]:
    query = select(Vote)
    return list(session.exec(query).all())


def create_vote(vote: Vote, session: Session) -> Vote:
    session.add(vote)
    session.commit()
    session.refresh(vote)
    return vote
