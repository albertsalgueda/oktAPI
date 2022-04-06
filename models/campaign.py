from pydantic import BaseModel, Field, validator

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

    budget: float = Field(None)  # represents daily budget
    spent: list = Field(None)  # represents total spent
    conversion_value: list = Field(None) #  represents Purchase Conversion Value


class CampaignUpdate(BaseModel):
    """Compaign update model."""

    id: int = Field(...)

    @validator("id")
    def id_must_be_exist(cls, v):
        if connector.collection(Collections.CAMPAIGN).find_one({"id": v}) is None:
            raise ValueError(f"{v} should be exist")
        return v

    budget: float = Field(None)  # represents daily budget
    spent: float = Field(None)  # represents total spent
    impressions: int = Field(None)
    conversions: int = Field(None)
    roas: float = Field(None)


class CampaignOut(BaseModel):
    """Fetching parameters from DB."""

    id: int = Field(...)
    budget: float = Field(None)  # represents daily budget
    spent: float = Field(None)  # represents total spent
    impressions: int = Field(None)
    conversions: int = Field(None)
    roas: float = Field(None)


class CampaignDB(BaseModel):
    """Mapping campaign attributes into campaign class."""

    id: int = Field(...)
    budget: float = Field(...)  # represents daily budget
    spent: float = Field(...)  # represents total spent
    impressions: int = Field(...)
    roas: float = Field(...)


class CampaignDelete(BaseModel):
    """Delete campaign model."""

    id: int = Field(...)

    @validator("id")
    def id_must_be_exist(cls, v):
        if connector.collection(Collections.CAMPAIGN).find_one({"id": v}) is None:
            raise ValueError(f"{v} not exist")
        return v
