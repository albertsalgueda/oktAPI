from pydantic import BaseModel, Field, validator
from typing import List
from utils.db_connector import DBConnector, Collections

connector = DBConnector()


class CampaignIn(BaseModel):
    """Incoming compaign model."""

    id: int = ...

    @validator("id")
    def id_must_be_unique(cls, v):
        c = connector.collection(Collections.CAMPAIGN).find_one({"id": v})
        if c:
            raise ValueError(f"{v} already exist")

        return v

    budget: float = Field(0)  # represents daily budget
    spent: List = Field([])  # represents total spent
    conversion_value: List = Field([]) #  represents Purchase Conversion Value

class CampaignUpdate(BaseModel):
    """Compaign update model."""
  
    spent: List = Field([])  # represents total spent
    conversion_value: List = Field([]) #  represents Purchase Conversion Value


class CampaignOut(BaseModel):
    """Fetching parameters from DB."""

    id: int = Field(...)
    budget: float = Field(...)  # represents daily budget
    spent: List = Field(...)  # represents total spent
    conversion_value: List = Field(...) 


class CampaignDB(BaseModel):
    """Mapping campaign attributes into campaign class."""

    id: int = Field(...)
    budget: float = Field(...)  # represents daily budget
    spent: List = Field(...)  # represents total spent
    conversion_value: List = Field(...)

class CampaignDelete(BaseModel):
    """Delete campaign model."""

    id: int = Field(...)

    @validator("id")
    def id_must_be_exist(cls, v):
        if connector.collection(Collections.CAMPAIGN).find_one({"id": v}) is None:
            raise ValueError(f"{v} not exist")
        states = connector.collection(Collections.STATE).find({})
        for state in states:
            if v in state.get("campaigns", []):
                raise ValueError("This campaign is already used by one of the state.")
        return v
