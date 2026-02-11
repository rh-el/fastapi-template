from typing import Annotated, List
import uuid

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_active_user, get_vote_service
from app.models.vote import VoteCreate, VoteResponse, VoteUpdate
from app.models.user import UserResponseWithId
from app.services.vote_service import VoteService

router = APIRouter(prefix="/vote", tags=["votes"])


@router.get("/", response_model=List[VoteResponse], status_code=200)
def get_all_votes(vote_service: VoteService = Depends(get_vote_service)):
    return vote_service.get_all_votes()


@router.get("/user/me", response_model=List[VoteResponse], status_code=200)
def get_my_votes(
    current_user: Annotated[UserResponseWithId, Depends(get_current_active_user)],
    vote_service: VoteService = Depends(get_vote_service),
):
    return vote_service.get_user_votes(current_user.id)


@router.get("/{vote_id}", response_model=VoteResponse, status_code=200)
def get_vote(
    vote_id: uuid.UUID,
    vote_service: VoteService = Depends(get_vote_service),
):
    return vote_service.get_vote(vote_id)


@router.post("/", response_model=VoteResponse, status_code=201)
def create_vote(
    vote_data: VoteCreate,
    current_user: Annotated[UserResponseWithId, Depends(get_current_active_user)],
    vote_service: VoteService = Depends(get_vote_service),
):
    return vote_service.create_vote(vote_data, current_user.id)


@router.put("/{vote_id}", response_model=VoteResponse, status_code=200)
def update_vote(
    vote_id: uuid.UUID,
    vote_data: VoteUpdate,
    current_user: Annotated[UserResponseWithId, Depends(get_current_active_user)],
    vote_service: VoteService = Depends(get_vote_service),
):
    return vote_service.update_vote(vote_id, vote_data, current_user.id)


@router.delete("/{vote_id}", status_code=200)
def delete_vote(
    vote_id: uuid.UUID,
    current_user: Annotated[UserResponseWithId, Depends(get_current_active_user)],
    vote_service: VoteService = Depends(get_vote_service),
):
    vote_service.delete_vote(vote_id, current_user.id)
    return {"message": "Vote successfully deleted"}
