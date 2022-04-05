from http.client import HTTPException
from os import stat
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
    static_dict = {
        "current_budget": state.budget / state.time,
        "remaining": state.budget,
        "k_arms": len(state.campaigns)
    }
    add = connector.collection(Collections.STATE).insert_one({**state.dict(), **static_dict})
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


@router.get("/state/{id}", description="get state by id", tags=["state"])
async def get_one_state(
    id: int,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """get state."""
    state = connector.collection(Collections.STATE).find_one({"id": id})
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
    if state is None:
        return {"success": False}
    state1 = StateOut(**state)
    # inital_allocation = [0.25, 0.25, 0.5]
    try:
        state = State(
            state1
        )
        ai = AI(id, state, 10, 10)
        d = ai.act()
        state = connector.collection(Collections.STATE).find_one({"id": id})
        state2 = StateOut(**state)
    except Exception as err:
        return {"message": f"{err}"}
    return {
        "remaining budget": state2.remaining,
        "current time": state2.current_time,
        "budget allocation": state2.budget_allocation,
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
