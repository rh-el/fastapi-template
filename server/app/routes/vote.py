from typing import List
from fastapi import APIRouter, Depends

from app.core.dependencies import get_vote_service
from app.models.vote import Role, VoteResponse
from app.services.vote_service import VoteService

router = APIRouter(prefix="/vote", tags=["votes"])


@router.get("/", response_model=List[VoteResponse], status_code=200)
def get_all_votes(vote_service: VoteService = Depends(get_vote_service)):
    return vote_service.get_all_votes()


@router.post("/{role}", status_code=201)
def create_vote(
    role: Role,
    vote_service: VoteService = Depends(get_vote_service),
):
    vote_service.create_vote(role)
    return {"message": f"{role.value} vote recorded"}
