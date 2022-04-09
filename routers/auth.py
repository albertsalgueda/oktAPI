"""Provide authentication related endpoints."""

import jwt
from datetime import datetime, timedelta
from typing import List
from passlib.context import CryptContext
from fastapi import Depends, APIRouter, HTTPException
from fastapi.param_functions import Form
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi import Security

from utils.db_connector import DBConnector, Collections
from models.user import User, UserDB, Token, AccountSettingsIn

router = APIRouter()
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
connector = DBConnector()
SECRET_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTY3OTIxNTgyOCwiaWF0IjoxNjQ3Njc5ODI4fQ.CsiLDgUPYIziWnlUeOYMP2yaz10eSoDE3We24I0eNUY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth",
    scopes={
        "read": "Read API.",
        "write": "Write API.",
        "me": "Change account settings.",
        "admin": "Admin access.",
        "api": "Client ID generation access."
    }
)

async def _get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    allow_on_first_login: bool = False,
) -> User:
    """Get current user.

    Args:
        security_scopes (SecurityScopes): Security scopes required.
        token (str, optional): token. Defaults to Depends(oauth2_scheme).

    Returns:
        User: the owner of the token.
    """

    cred_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials."
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise cred_exception
        scopes = payload.get("scopes", [])
        print(scopes)
        for scope in security_scopes.scopes:
            if scope not in scopes:
                raise HTTPException(403, "Not enough permission.")

        user = connector.collection(Collections.USERS).find_one(
            {"username": username}
        )
        if user is None:
            raise cred_exception
        if user["firstLogin"] and not allow_on_first_login:
                raise HTTPException(
                    401, "Change the password before using this endpoint."
                )
        return User(
            username=username,
            scopes=scopes,
            firstLogin=user["firstLogin"]
        )
    except jwt.PyJWTError:
        raise cred_exception

async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
):
    """Do not allow first time users."""
    return await _get_current_user(
        security_scopes, token, allow_on_first_login=False
    )


async def first_time_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
):
    """Allow first time users."""
    return await _get_current_user(
        security_scopes, token, allow_on_first_login=True
    )

class OAuth2PasswordRequestForm:
    """Credential request form."""

    def __init__(
        self,
        grant_type: str = Form(
            "password", regex="password|client_credentials"
        ),
        username: str = Form(None),
        password: str = Form(None),
        client_id: str = Form(None),
        client_secret: str = Form(None),
        scope: str = Form(""),
    ):
        """Initialize."""
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


@router.post(
    "/auth",
    response_model=Token,
    tags=["Authentication"],
    description="Get authentication token.",
)
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Generate new authentication token.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): Form data. Defaults to Depends().

    Returns:
        Token: Generated authentication token.
    """
    try:
        if form_data.grant_type == "password":
            if form_data.username and form_data.password:
                user = connector.collection(Collections.USERS).find_one(
                    {"username": form_data.username}, {"_id": 0}
                )
                if user is None or not crypt_context.verify(
                    form_data.password, user["password"], scheme="bcrypt"
                ):
                    raise HTTPException(401, "Incorrect username or password.")
            else:
                raise HTTPException(401, "Incorrect username or password.")
        elif form_data.grant_type == "client_credentials":
            if form_data.client_id and form_data.client_secret:
                user = connector.collection(Collections.USERS).find_one(
                    {
                        "tokens": {
                            "$elemMatch": {
                                "client_id": form_data.client_id,
                                "client_secret": form_data.client_secret,
                            }
                        }
                    }
                )
                if user is not None:
                    token = list(
                        filter(
                            lambda x: x["client_id"] == form_data.client_id,
                            user["tokens"],
                        )
                    ).pop()
                if not user or (
                    token["expiresAt"] is not None
                    and datetime.now() > token["expiresAt"]
                ):
                    raise HTTPException(
                        401, "Invalid client_id/client_secret provided."
                    )
            else:
                raise HTTPException(
                    401, "Invalid client_id/client_secret provided."
                )
        else:
            raise HTTPException(422, "grant_type not supported.")
        if form_data.scopes:  # verify scopes if any
            for scope in form_data.scopes:
                if scope not in user["scopes"]:
                    raise HTTPException(403, "Unauthorized")
            granted_scopes = form_data.scopes
        else:
            # if no scopes specified; grant all of allowed scopes
            granted_scopes = user["scopes"]
        print(
            f"Authentication token generated for user {form_data.username}."
        )
        return {
            "access_token": jwt.encode(
                {
                    "username": user["username"],
                    "scopes": granted_scopes,
                    "exp": datetime.utcnow()
                    + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                },
                SECRET_KEY,
                ALGORITHM,
            ),
            "token_type": "bearer",
            "scopes": granted_scopes,
            "firstLogin": user["firstLogin"],
        }
    except ValueError:
        raise HTTPException(400, "Could not verify username and password.")

@router.patch(
    "/account", tags=["Authentication"], description="Update account settings."
)
async def update_account_settings(
    settings: AccountSettingsIn,
    user: User = Security(
        first_time_user,
        scopes=["me"],
    ),
):
    """Update the settings.

    Args:
        settings (SettingsIn): The settings object.
        user (User, optional): The user object. Defaults to Security(get_current_user, scopes=["write"]).
    """
    msg = "false"
    set_dict = {}
    user_dict = connector.collection(Collections.USERS).find_one(
        {"username": user.username}
    )
    if user_dict is None:
        raise HTTPException(400, "Could not update the password.")
    if not crypt_context.verify(settings.oldPassword, user_dict["password"]):
        raise HTTPException(400, "Incorrect password.")
    if settings.oldPassword == settings.newPassword:
        raise HTTPException(
            400, "New password can not be same as the old password."
        )
    set_dict["password"] = crypt_context.hash(settings.newPassword)
    if set_dict != {}:  # i.e. the password was updated
        if user.firstLogin:
            set_dict["firstLogin"] = False
        connector.collection(Collections.USERS).update_one(
            {"username": user.username}, {"$set": set_dict}
        )
        msg = f"Password changed for the {user.username} user."
    return {"msg": msg}