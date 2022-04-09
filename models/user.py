"""Provides user related models."""

from passlib.context import CryptContext
from typing import List
from enum import Enum
from pydantic import BaseModel, Field, validator

from utils.db_connector import DBConnector, Collections

connector = DBConnector()
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    "Auth token model."

    username: str
    scopes: List[str]
    firstLogin: bool = Field(True)

class SecurityScopes(str, Enum):
    """Enumeration for allowed scopes."""

    admin = "admin"
    api = "api"
    read = "read"
    write = "write"
    me = "me"

class UserOut(BaseModel):
    """The outgoing user model."""

    username: str = Field(...)
    scopes: List[SecurityScopes] = Field(...)

def _validate_scopes(scopes: List[SecurityScopes]):
    """Validate security scopes."""

    if SecurityScopes.admin in scopes:
        raise ValueError("can not create new user with admin scope.")
    elif SecurityScopes.me not in scopes:
        scopes.append(SecurityScopes.me)

class UserIn(BaseModel):
    """The incoming user model."""

    username: str = Field(...)
    password: str = Field(...)
    scopes: List[SecurityScopes] = Field(...)

    @validator("username")
    def username_must_be_unique(cls, v: str):
        """Validate that the username is unique."""

        if (
            connector.collection(Collections.USERS).find_one({"username": v})
            is not None
        ):
            raise ValueError("Username already exists.")

        return v

    @validator("password")
    def hash_password(cls, v:str):
        """validate password."""

        if len(v) < 8:
            raise ValueError("Password length must be atleast 8 char.")
        return crypt_context.hash(v)

    @validator("scopes")
    def scope_validaton(cls, v: str):
        """Validate scope."""

        _validate_scopes(v)
        return v

class UserUpdate(BaseModel):
    """The update user model."""

    username: str = Field(...)
    password: str = Field(None)
    scopes: List[SecurityScopes] = Field(None)

    @validator("username")
    def username_must_exist(cls, v: str):
        """Validate that the username is unique."""

        user = connector.collection(Collections.USERS).find_one({"username": v})

        if user is None:
            raise ValueError("Username does not exists.")
        elif "admin" in user["scopes"]:
            raise ValueError("can not modify admin user.")

        return v

    @validator("scopes")
    def scope_validaton(cls, v: str):
        """Validate scope."""
        if v is None:
            return v
        _validate_scopes(v)
        return v

    @validator("password")
    def hash_password(cls, v:str):
        """validate password."""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password length must be atleast 8 char.")
        return crypt_context.hash(v)

class UserDelete(BaseModel):
    """The delete user model."""

    username: str = Field(...)

    @validator("username")
    def username_must_exist(cls, v: str):
        user = connector.collection(Collections.USERS).find_one({"username": v})

        if user is None:
            raise ValueError("username does not exist.")
        elif "admin" == user["scopes"]:
            raise ValueError("can not delete admin user.")

        return v

class UserDB(BaseModel):
    """The database user model."""
    username: str = Field(...)
    password: str = Field(None)
    scopes:  List[str] = []
    tokens: List = []
    firstLogin: bool = Field(True)

class TokenDelete(BaseModel):
    """Token delete model."""

    client_id: str = Field(...)

class Token(BaseModel):
    """Access token model for OAuth 2.0."""

    access_token: str
    token_type: str
    scopes: List[str]
    firstLogin: bool

class AccountSettingsIn(BaseModel):
    """The incoming account settings model."""

    oldPassword: str = Field(...)
    newPassword: str = Field(...)