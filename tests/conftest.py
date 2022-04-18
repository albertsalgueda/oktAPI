import asyncio
import pytest
import mongomock
import pymongo

from utils.db_connector import DBConnector, Collections


@pytest.fixture(scope="session")
def endpoints():
    return {
        "base": "http://localhost:8000",
        }

@pytest.fixture(scope="session")
def run():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete


@pytest.fixture(scope="session")
def db():  # NOSONAR: S1542
    return DBConnector()


@mongomock.patch(servers=(("localhost", 27017),))
def init_db():
    connector = DBConnector()
    # replace the actual client with the mock one
    connector._client = pymongo.MongoClient("localhost", 27017)
    connector.collection(Collections.USERS).insert_one(
        {
            "username": "admin",
            "password": "$2y$12$hwULodJIcg6ncfRgjWkqnOcJFEcSEk3zMiIyjxQLgRZwXbROVilF.",
            "scopes": ["read", "write", "me"],
            "firstLogin": True,
        }
    )

def pytest_sessionstart(session):
    init_db()
