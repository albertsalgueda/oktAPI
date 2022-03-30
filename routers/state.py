from fastapi import APIRouter, Security, Query
from typing import List

from main import AI
from .auth import get_current_user
from utils.db_connector import DBConnector, Collections
from models.state import (
    StateIn,
    StateDB,
    StateOut,
    StateDelete,
    StateUpdate
)
from models.user import User
from main import State


router = APIRouter()
connector = DBConnector()


@router.post("/state", description="Create state", tags=["state"])
async def create_state(
    state: StateIn,
    user: User = Security(get_current_user, scopes=["write"]),
):
    """Create state."""
    add = connector.collection(Collections.STATE).insert_one(
        state.dict()
    )
    return {"success": True}

@router.get("/state", description="Get State.", tags=["state"])
async def get_state(
    user: User = Security(get_current_user, scopes=["read"]),
):
    """Get state."""
    return [
        StateOut(**state)
        for state in connector.collection(Collections.STATE).find({})
    ]

@router.delete("/state", description="Delete state.", tags=["state"])
async def delete_state(
    state: StateDelete,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """delete state."""
    connector.collection(Collections.STATE).delete_one({
        "id": state.id
    })
    return {"success": True}

@router.post(
    "/state/{id}", description="get state by id", tags=["state"]
)
async def get_one_state(
    id: int,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """get state."""
    state = connector.collection(Collections.STATE).find({"id": id})
    if state is None:
        return {
            "success": False,
            "message": f"this state with {id} doesn't exist.",
        }
    return StateOut(**state)

@router.get(
    "/state/{id}/next", description="Get budget allocation.", tags=["state"] 
)
async def get_budget(
    id: int,
    budget: float,
    time: int,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """add method."""
    state = connector.collection(Collections.STATE).find_one({"id": id})
    state = StateOut(**state)
    state = State(budget, time, state.campaigns, 0)
    ai = AI(state, budget, time)
    optimistic_agent_result = ai.act()
    total_rewards = sum(optimistic_agent_result["rewards"])
    return total_rewards
    #TODO. What should we return on this?


@router.get('/state/{id}/budget', description="Get budget.", tags=["state"])
def get_budget_allocation(
    id: int,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """Return budget allocation."""
    state = connector.collection(Collections.STATE).find_one({"id": id})
    state = StateOut(**state)
    return state.budget_allocation