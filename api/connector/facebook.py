from api.config import Config

from api.models.connector import AdAccount
from api.core.static_data import ChannelType, facebook_metrics, facebook_dimensions
from api.models.user import User
from api.core.auth import get_current_user
from api.database.database import session
from api.database.models import UserDB
from api.models.data import FieldOption

from fastapi import APIRouter, Request, HTTPException
import requests
from starlette.responses import RedirectResponse
from typing import List


DOMAIN_URL = Config.DOMAIN_URL
FB_CLIENT_SECRET = Config.FB_CLIENT_SECRET
CLIENT_URL = Config.CLIENT_URL

router = APIRouter(prefix="/facebook")


@router.get("/login")
def login(request: Request):
    app_id = 3796703967222950
    code = request.query_params["code"]
    token = request.query_params["state"]

    redirect_uri = f"{DOMAIN_URL}/connector/facebook/login/"
    redirect_uri = redirect_uri.replace("www.", "")
    auth_url = f"https://graph.facebook.com/v17.0/oauth/access_token?client_id={app_id}&redirect_uri={redirect_uri}&code={code}&client_secret={FB_CLIENT_SECRET}"

    # Save the access token to the user's database.
    response = requests.get(auth_url)

    json = response.json()
    try:
        access_token = json["access_token"]
    except KeyError as e:
        print(json)
        raise HTTPException(
            status_code=400,
            detail=f"Could not get access token from Facebook. Error {e}. Response: {json}",
        )

    # Commit access_token to the database.
    user: User = get_current_user(token)

    try:
        user = session.query(UserDB).filter(UserDB.email == user.email).first()
        user.facebook_refresh_token = access_token
        session.add(user)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise HTTPException(
            status_code=400, detail=f"Could not save access token to database. {e}"
        )
    finally:
        session.close()
        session.remove()

    redirect_client_url = f"{CLIENT_URL}/add-data-source/"

    return RedirectResponse(url=redirect_client_url)


@router.get("/ad_accounts", response_model=List[AdAccount])
def ad_accounts(token: str):
    current_user: User = get_current_user(token)
    adaccounts = []

    url = f"https://graph.facebook.com/v17.0/me?fields=adaccounts&access_token={current_user.facebook_access_token}"
    response = requests.get(url)
    json = response.json()
    accounts = json["adaccounts"]["data"]

    for account in accounts:
        id = account["id"]
        account_id = account["account_id"]
        url = f"https://graph.facebook.com/v17.0/{id}?fields=name&access_token={current_user.facebook_access_token}"
        response = requests.get(url)
        json = response.json()
        name = json["name"]

        adaccount: AdAccount = AdAccount(
            id=id,
            channel=ChannelType.facebook,
            account_id=account_id,
            name=name,
            img="facebook-icon",
        )
        adaccounts.append(adaccount)

    return adaccounts


@router.get("/fields", response_model=List[FieldOption])
def fields(
    default: bool = False, metrics: bool = False, dimensions: bool = False
) -> List[FieldOption]:
    fields_options = None
    if metrics:
        fields_options = facebook_metrics
    elif dimensions:
        fields_options = facebook_dimensions
    else:
        fields_options = facebook_metrics + facebook_dimensions

    if default:
        fields_options = [f for f in fields_options if f["default"]]

    return fields_options


@router.get("/delete")
def delete():
    return {"success": 200}


@router.get("/deauthorize")
def deauthorize():
    {"success": 200}
