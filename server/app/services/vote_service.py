import uuid
from typing import List

from sqlmodel import Session

from app.core.exceptions import ResourceNotFoundException, VoteAccessDeniedException
from app.crud.vote_crud import (
    create_vote,
    delete_vote,
    get_all_votes,
    get_user_votes,
    get_vote,
    update_vote,
)
from app.models import Vote
from app.models.vote import VoteCreate, VoteResponse, VoteUpdate


class VoteService:
    def __init__(self, session: Session):
        self.session = session

    def get_all_votes(self) -> List[VoteResponse]:
        votes = get_all_votes(self.session)
        return [VoteResponse(**v.model_dump()) for v in votes]

    def get_vote(self, vote_id: uuid.UUID) -> VoteResponse:
        vote = get_vote(vote_id, self.session)
        if not vote:
            raise ResourceNotFoundException("vote", vote_id)
        return VoteResponse(**vote.model_dump())

    def get_user_votes(self, user_id: uuid.UUID) -> List[VoteResponse]:
        votes = get_user_votes(user_id, self.session)
        return [VoteResponse(**v.model_dump()) for v in votes]

    def create_vote(self, vote_data: VoteCreate, user_id: uuid.UUID) -> VoteResponse:
        new_vote = Vote(
            title=vote_data.title,
            description=vote_data.description,
            user_id=user_id,
        )
        created = create_vote(new_vote, self.session)
        return VoteResponse(**created.model_dump())

    def update_vote(
        self, vote_id: uuid.UUID, vote_data: VoteUpdate, user_id: uuid.UUID
    ) -> VoteResponse:
        vote = get_vote(vote_id, self.session)
        if not vote:
            raise ResourceNotFoundException("vote", vote_id)
        if vote.user_id != user_id:
            raise VoteAccessDeniedException(vote_id)

        for key, value in vote_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(vote, key, value)

        updated = update_vote(vote, self.session)
        return VoteResponse(**updated.model_dump())

    def delete_vote(self, vote_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        vote = get_vote(vote_id, self.session)
        if not vote:
            raise ResourceNotFoundException("vote", vote_id)
        if vote.user_id != user_id:
            raise VoteAccessDeniedException(vote_id)
        return delete_vote(vote, self.session)
