from pydantic import BaseModel, Field, validator
from typing import Dict, List
from oktFastAPI.models.state import StateDB
from utils.db_connector import DBConnector, Collections


connector = DBConnector()

class AiIn(BaseModel):
    id: int
    env: StateDB
    initial_q: float
    initial_visits: float
    q_values: List
    arm_count: List
    rewards : List = Field([0.0])
    cum_rewards: List = Field([0.0])

