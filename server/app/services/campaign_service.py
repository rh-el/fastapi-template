from typing import List
import uuid

from sqlmodel import Session
from app.core.exceptions import CampaignNotFoundException
from app.crud.campaign_crud import (
    create_campaign,
    get_all_campaigns,
    get_campaign_by_id,
)
from app.models.campaign import CampaignCreate, CampaignResponse


class CampaignService:
    def __init__(self, session: Session):
        self.session = session

    def create_campaign(self, campaign_data: CampaignCreate) -> CampaignResponse:
        campaign = create_campaign(campaign_data, self.session)
        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            interaction_config=campaign.interaction_config or [],
            qr_base_url=campaign.qr_base_url,
            is_active=campaign.is_active,
            created_at=campaign.created_at,
        )

    def get_campaign(self, campaign_id: uuid.UUID) -> CampaignResponse:
        campaign = get_campaign_by_id(campaign_id, self.session)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)
        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            interaction_config=campaign.interaction_config or [],
            qr_base_url=campaign.qr_base_url,
            is_active=campaign.is_active,
            created_at=campaign.created_at,
        )

    def get_all_campaigns(self) -> List[CampaignResponse]:
        campaigns = get_all_campaigns(self.session)
        return [
            CampaignResponse(
                id=c.id,
                name=c.name,
                description=c.description,
                interaction_config=c.interaction_config or [],
                qr_base_url=c.qr_base_url,
                is_active=c.is_active,
                created_at=c.created_at,
            )
            for c in campaigns
        ]
