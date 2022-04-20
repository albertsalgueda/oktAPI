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
    "/state/{id}/next", description="Calls AI() to get a new budget allocation. Please update campaign data before calling this endpoint.", tags=["state"]
)
async def get_new_allocation(
    id: int,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """
    We map a State based on ID and user. User X, state.id = 0 ||| User Y, state.id = 0 
    #TODO -> Each user has a different DB table.  
    """
    state = connector.collection(Collections.STATE).find_one({"id": id}) # get state object

    if state is None:
        return {"success": False}

    state1 = StateOut(**state) # mapping fields from db to state out

    try:
        state = State(
            state1
        )
        ai = AI(id, state, 1, 10) 
        d = ai.act() 
        state = connector.collection(Collections.STATE).find_one({"id": id}) #Checking State Object 
        state2 = StateOut(**state)
    except Exception as err:
        return {"message": f"{err}"}
    return {
        "current budget": state2.current_budget,
        "current time": state2.current_time,
        "budget allocation": state2.budget_allocation,
        "remaining budget": state2.remaining
    }

@router.get("/state/{id}/budget", description="Returns campaign's daily budget.", tags=["state"])
def get_daily_budget(
    id: int,
    user: User = Security(get_current_user, scopes=["read"]),
):
    """Return daily budget allocation."""
    daily_allocation = {}
    state = connector.collection(Collections.STATE).find_one({"id": id})
    state = StateOut(**state)
    for id in state.campaigns:
        campaign = connector.collection(Collections.CAMPAIGN).find_one({"id": id})
        daily_allocation[str(id)] = campaign.get("budget", 0)
    return daily_allocation

