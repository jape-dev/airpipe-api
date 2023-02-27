from api.config import Config
from api.utilities.google.auth import authorize, oauth2callback
from api.utilities.google.ga_runner import REFRESH_ERROR

from fastapi import APIRouter, Request
import json
from starlette.responses import RedirectResponse

CLIENT_URL = Config.CLIENT_URL

router = APIRouter(prefix="/google")


@router.get("/auth")
def auth(request: Request) -> RedirectResponse:
    token = request.query_params["token"]
    request.session["token"] = token
    auth_info = authorize()
    passthtough_val = auth_info["passthrough_val"]
    request.session["passthrough_val"] = passthtough_val
    url = auth_info["authorization_url"]
    return RedirectResponse(url=url)


@router.get("/oauth2_callback")
def oauth2_callback(request: Request) -> RedirectResponse:
    token = request.session["token"]
    state = request.query_params["state"]
    code = request.query_params["code"]
    passthrough_val = request.session["passthrough_val"]
    oauth2callback(passthrough_val, state, code, token)
    return RedirectResponse(url=CLIENT_URL)


@router.get("/metrics")
def metrics(request: Request):
    headers = request.headers
    token = headers["token"]
    try:
        x = 5
        # get metrics somehow
    except Exception as ex:
        return handleGoogleTokenException(ex)


def handleGoogleTokenException(ex):
    error = str(ex)
    if error == REFRESH_ERROR:
        return json.dumps(
            {"code": 401, "name": "INVALID REFRESH TOKEN", "description": error}
        )
    else:
        return json.dumps(
            {"code": 500, "name": "INTERNAL SERVER ERROR", "description": error}
        )
