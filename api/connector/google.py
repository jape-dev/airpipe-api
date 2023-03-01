from api.config import Config
from api.core.auth import get_current_user
from api.database.database import session
from api.utilities.google.auth import authorize, oauth2callback
from api.utilities.google.ga_runner import REFRESH_ERROR, create_client
from api.database.models import UserDB
from api.models.user import User
from api.models.google import AdAccount, GoogleQuery, GoogleQueryResults

from fastapi import APIRouter, Request, HTTPException
from typing import List

import json
from starlette.responses import RedirectResponse

CLIENT_URL = Config.CLIENT_URL

router = APIRouter(prefix="/google")


@router.get("/auth")
def auth(request: Request) -> RedirectResponse:
    token = request.query_params["token"]
    google_token = request.query_params["googleToken"]
    request.session["token"] = token
    request.session["google_token"] = google_token
    auth_info = authorize()
    passthtough_val = auth_info["passthrough_val"]
    request.session["passthrough_val"] = passthtough_val
    url = auth_info["authorization_url"]
    return RedirectResponse(url=url)


@router.get("/oauth2_callback")
def oauth2_callback(request: Request) -> RedirectResponse:
    google_token = request.session["google_token"]
    token = request.session["token"]
    state = request.query_params["state"]
    code = request.query_params["code"]
    passthrough_val = request.session["passthrough_val"]
    oauth2callback(passthrough_val, state, code, google_token)
    # Commit access_token to the database.
    user: User = get_current_user(token)
    user = session.query(UserDB).filter(UserDB.email == user.email).first()
    user.google_access_token = google_token
    try:
        session.add(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Could not save google access token to database. {e}",
        )
    finally:
        session.close()
    return RedirectResponse(url=CLIENT_URL)


@router.get("/ad_accounts", response_model=List[AdAccount])
def ad_accounts(token: str):
    try:
        client = create_client(token)
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        resource_names = [
            AdAccount(id=int(resource_name.replace("customers/", "")))
            for resource_name in accessible_customers.resource_names
        ]
        return resource_names
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
