from fastapi import APIRouter, Security, Query
from typing import List

from .auth import get_current_user
from utils.db_connector import DBConnector, Collections
from models.campaign import (
    CampaignIn,
    CampaignOut,
    CampaignUpdate,
    CampaignDelete,
)
from models.user import User

router = APIRouter()
connector = DBConnector()


@router.get(
    "/campaigns", description="Get list of campaigns", tags=["campaigns"]
)
async def get_campaigns(
    user: User = Security(get_current_user, scopes=["read"])
) -> List[CampaignOut]:
    """List campaigns."""
    return [
        CampaignOut(**campaign)
        for campaign in connector.collection(Collections.CAMPAIGN).find({})
    ]


@router.get(
    "/campaign/{id}", description="get campaign by id", tags=["campaigns"]
)
async def get_one_campaign(
    id: int,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """Create campaign."""
    campaign = connector.collection(Collections.CAMPAIGN).find_one({"id": id})
    if campaign is None:
        return {
            "success": False,
            "message": f"this campaign with {id} doesn't exist.",
        }
    return CampaignOut(**campaign)


@router.post("/campaign", description="Create campaigns", tags=["campaigns"])
async def create_campaigns(
    campaign: CampaignIn,
    user: User = Security(get_current_user, scopes=["write"]),
):
    """Create campaign."""
    print(campaign.dict())
    add = connector.collection(Collections.CAMPAIGN).insert_one(
        campaign.dict()
    )
    return {"success": True}


@router.delete("/campaign", description="delete campaigns", tags=["campaigns"])
async def delete_campaigns(
    campaign: CampaignDelete,
    user: User = Security(get_current_user, scopes=["write"]),
):
    """delete campaign."""
    connector.collection(Collections.CAMPAIGN).delete_one({"id": campaign.id})
    return {"success": True}


@router.patch("/campaign", description="update campaigns", tags=["campaigns"])
async def update_campaigns(
    campaign: CampaignUpdate,
    user: User = Security(get_current_user, scopes=["write"]),
):
    """update campaign."""
    connector.collection(Collections.CAMPAIGN).replace_one(
        {"id": campaign.id}, campaign.dict()
    )
    return {"success": True}
