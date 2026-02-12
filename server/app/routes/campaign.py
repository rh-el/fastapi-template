from typing import List
import uuid
from fastapi import APIRouter, Depends

from app.core.dependencies import get_campaign_service
from app.models.campaign import CampaignCreate, CampaignResponse
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaign", tags=["campaigns"])


@router.post("/", response_model=CampaignResponse, status_code=201)
def create_campaign(
    campaign: CampaignCreate,
    campaign_service: CampaignService = Depends(get_campaign_service),
):
    return campaign_service.create_campaign(campaign)


@router.get("/", response_model=List[CampaignResponse], status_code=200)
def get_all_campaigns(
    campaign_service: CampaignService = Depends(get_campaign_service),
):
    return campaign_service.get_all_campaigns()


@router.get("/{campaign_id}", response_model=CampaignResponse, status_code=200)
def get_campaign(
    campaign_id: uuid.UUID,
    campaign_service: CampaignService = Depends(get_campaign_service),
):
    return campaign_service.get_campaign(campaign_id)
