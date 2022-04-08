from fastapi import FastAPI
from common.models import ErrorMessage
from routers import campains, auth, users, state
from fastapi import Depends, FastAPI

API_PREFIX = "/api"
okt = {'name':'Oktopus','url':'https://www.oktopus.io/contact'}

app = FastAPI(
    title="Budget Optimization API",
    description = "Welcome! To test our API for free, contact us and you will be given a username and password.",
    version="1.0.0",
    contact = okt,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

common_response = {
    "400": {"model": ErrorMessage},
    "401": {"model": ErrorMessage},
    "403": {"model": ErrorMessage},
    "405": {"model": ErrorMessage},
    "429": {"model": ErrorMessage},
    "500": {"model": ErrorMessage},
}


app.include_router(auth.router, responses=common_response, prefix=API_PREFIX)
app.include_router(users.router, responses=common_response, prefix=API_PREFIX)
app.include_router(campains.router, responses=common_response, prefix=API_PREFIX)
app.include_router(state.router, responses=common_response, prefix=API_PREFIX)
