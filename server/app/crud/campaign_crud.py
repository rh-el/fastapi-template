from typing import List, Optional
import uuid

from sqlmodel import Session, select
from app.models import Campaign
from app.models.campaign import CampaignCreate


def create_campaign(campaign_data: CampaignCreate, session: Session) -> Campaign:
    campaign = Campaign(
        name=campaign_data.name,
        description=campaign_data.description,
        interaction_config=campaign_data.interaction_config,
        qr_base_url=campaign_data.qr_base_url,
    )
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    return campaign


def get_campaign_by_id(campaign_id: uuid.UUID, session: Session) -> Optional[Campaign]:
    return session.exec(select(Campaign).where(Campaign.id == campaign_id)).first()


def get_all_campaigns(session: Session) -> List[Campaign]:
    return list(session.exec(select(Campaign)).all())
