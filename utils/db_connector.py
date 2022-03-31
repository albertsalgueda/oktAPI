import sys
from sys import stderr
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from enum import Enum
from .singleton import Singleton


class Collections(str, Enum):
    USERS = "users"
    CAMPAIGN = "campaign"
    STATE = "state"
    AI = "ai"


class DBConnector(metaclass=Singleton):

    def __init__(self):
        try:
            ### Add connection string of mongodb
            self._client = MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false")
        except KeyError as ex:
            print(ex, file=stderr)
            sys.exit(1)

    @property
    def database(self) -> Database:

        return self._client["budget"]

    def collection(self, name: Collections) -> Collection:
        
        return self.database[name]

