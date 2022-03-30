from fastapi import APIRouter, Security
from typing import List

from main import AI, Campaign
from .auth import get_current_user
from utils.db_connector import DBConnector, Collections
from models.state import StateIn, StateDB, StateOut, StateDelete, StateUpdate
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
    add = connector.collection(Collections.STATE).insert_one(state.dict())
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
    connector.collection(Collections.STATE).delete_one({"id": state.id})
    return {"success": True}


@router.post("/state/{id}", description="get state by id", tags=["state"])
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
    "/state/{id}/next", description="Get budget.", tags=["state"]
)
async def get_budget(
    id: int,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """add method."""
    state = connector.collection(Collections.STATE).find_one({"id": id})
    state1 = StateOut(**state)
    # inital_allocation = [0.25, 0.25, 0.5]
    state = State(
        state1.id,
        state1.budget,
        state1.time,
        state1.campaigns
    )
    ai = AI(state, state1.budget, state1.time)
    d = ai.act()
    print(d)
    state_update = StateUpdate(
        id=state.id,
        budget=state.budget,
        time=state.time,
        campaigns=state1.campaigns,
        current_time=state.current_time,
        current_budget=state.current_budget,
        history=state.history,
        budget_allocation=state.budget_allocation,
        remaining=state.remaining,
        step=state.step,
        k_arms=state.k_arms,
        stopped=state.stopped
    )
    connector.collection(Collections.STATE).replace_one(
        {"id": state_update.id}, state_update.dict()
    )
    return {
        "remaining budget": state.remaining,
        "current time": state.current_time,
        "budget allocation": state.budget_allocation,
    }


@router.get("/state/{id}/budget", description="Get budget allocation.", tags=["state"])
def get_budget_allocation(
    id: int,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """Return budget allocation."""
    state = connector.collection(Collections.STATE).find_one({"id": id})
    state = StateOut(**state)
    return state.budget_allocation
