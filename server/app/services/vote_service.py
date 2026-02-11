from typing import List
from sqlmodel import Session
from app.crud.vote_crud import (
    create_vote,
    get_all_votes,
)
from app.models import Vote
from app.models.vote import Role, VoteResponse

class VoteService:
    def __init__(self, session: Session):
        self.session = session

    def get_all_votes(self) -> List[VoteResponse]:
        votes = get_all_votes(self.session)
        return [VoteResponse(**v.model_dump()) for v in votes]

    def create_vote(self, role: Role) -> VoteResponse:
        created = create_vote(Vote(role=role), self.session)
        return VoteResponse(**created.model_dump())