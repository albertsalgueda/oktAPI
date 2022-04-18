import pytest
from utils.db_connector import DBConnector, Collections
from models.campaign import CampaignIn
from routers.campains import create_campaigns

def test_create_campaign(db: DBConnector, run):
    campaign = CampaignIn(id=0)

    # adding campaign with 0 id.
    run(create_campaigns(campaign))

    # campaign should exist in database.
    assert (
        db.collection(Collections.CAMPAIGN).find_one({"id": 0})
        is not None
    )