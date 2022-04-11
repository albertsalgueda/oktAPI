from pydantic import BaseModel, Field, validator
from typing import Dict, List
from utils.db_connector import DBConnector, Collections
from .campaign import CampaignDB

connector = DBConnector()


class StateIn(BaseModel):
    """Incoming state model."""

    id: int = Field(...)

    @validator("id")
    def id_must_be_unique(cls, v):
        if (
            connector.collection(Collections.STATE).find_one({"id": v})
            is not None
        ):
            raise ValueError(f"{v} already exist")
        
        return v

    budget: float = Field(None)
    time: int = Field(None)
    campaigns: List = Field([])

    @validator("campaigns")
    def validate_campaigns(cls, v):
        states = connector.collection(Collections.STATE).find({})
        for ids in v:
            if connector.collection(Collections.CAMPAIGN).find_one({"id": ids}) is None:
                raise ValueError(f"This id {ids} with campaign does not exist.")
            for state in states:
                if ids in state.get("campaigns", []):
                    raise ValueError(f"This campaign already used by other state.")
        return v
    current_time: int = Field(None) #TODO
    history: Dict = Field({}) 
    budget_allocation: Dict = Field({})
    step: float = 0.005
    stopped: List = Field([])

class StateUpdate(BaseModel):
    """Updating state model."""

    id: int = Field(...)

    @validator("id")
    def id_must_be_exist(cls, v):
        if connector.collection(Collections.STATE).find_one({"id": v}) is None:
            raise ValueError(f"{v} Should exist")
        return v

    budget: float = Field(None)
    time: int = Field(None)
    campaigns: List = Field([])

    @validator("campaigns")
    def validate_campaigns(cls, v):
        for ids in v:
            if connector.collection(Collections.CAMPAIGN).find_one({"id": ids}) is None:
                raise ValueError(f"This id {ids} with campaign does not exist.")
        return v

    current_time: int = Field(None)
    current_budget: float = Field(None)
    history: Dict = Field({})
    budget_allocation: Dict = Field({})
    remaining: float = Field(None)
    step: float = 0.005
    k_arms: int = Field(None)
    stopped: List = Field(None)


class StateOut(BaseModel):
    """Outcoming state model."""

    id: int = Field(...)
    budget: float = Field(None)
    time: int = Field(None)
    campaigns: List = Field([])
    current_time: int = Field(None)
    current_budget: float = Field(None)
    history: Dict = Field({})
    budget_allocation: Dict = Field({})
    remaining: float = Field(None)
    step: float = 0.005
    k_arms: int = Field(None)
    stopped: List = Field(None)


class StateDB(BaseModel):
    """DB of state."""

    id: int = Field(...)
    budget: float = Field(...)
    time: int = Field(...)
    campaigns: List = Field([])
    current_time: int = Field(...)
    current_budget: float = Field(None)
    history: Dict = Field({})
    budget_allocation: Dict = Field({})
    remaining: float = Field(None)
    step: float = 0.005
    k_arms: int = Field(None)
    stopped: List = Field(None)


class StateDelete(BaseModel):
    """Delete of state model."""

    id: int = Field(...)

    @validator("id")
    def id_must_be_exist(cls, v):
        if connector.collection(Collections.STATE).find_one({"id": v}) is None:
            raise ValueError(f"{v} not exist")
        return v
