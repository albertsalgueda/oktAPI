from typing import List
from pydantic import BaseModel, Field, validator

class Campaign(BaseModel):
    id: int = Field(...)
    budget: float  #represents daily budget
    spent: float #represents total spent
    impressions: int
    conversions: int
    roas: float

class State(BaseModel):
    id: int = Field(...)
    budget:  float
    time: int
    campaigns: List[Campaign]

    @validator("campaigns")
    def validate_campaigns(cls, v):
        if len(v) == 0:
            raise ValueError("Campaigns should not be empty.")
        return v
    current_time: int
