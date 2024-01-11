from api.config import Config

from api.models.connector import AdAccount
from api.core.static_data import ChannelType, instagram_account_metrics, instagram_account_dimensions, instagram_media_dimensions, instagram_media_metrics
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

router = APIRouter(prefix="/instagram")


@router.get("/login")
def login(request: Request):
    app_id = 1190161828611459
    code = request.query_params["code"]
    token = request.query_params["state"]

    redirect_uri = f"{DOMAIN_URL}/connector/instagram/login/"
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
            detail=f"Could not get access token from Instagram. Error {e}. Response: {json}",
        )

    # Commit access_token to the database.
    user: User = get_current_user(token)

    try:
        user = session.query(UserDB).filter(UserDB.email == user.email).first()
        user.instagram_access_token = access_token
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

    url = f"https://graph.facebook.com/v17.0/me/accounts?access_token={current_user.facebook_access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        json = response.json()
        accounts = json["data"]
        account_ids = [account["id"] for account in accounts]
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Could not get instagram accounts. {response.text}",
        )
    
    instagram_account_ids = []
    for id in account_ids:
        url = f"https://graph.facebook.com/v18.0/{id}?fields=instagram_business_account&access_token={current_user.facebook_access_token}"
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
            id = json["instagram_business_account"]["id"]
            instagram_account_ids.append(id)

    for id in instagram_account_ids:
        url = f"https://graph.facebook.com/v17.0/{id}?fields=username&access_token={current_user.facebook_access_token}"
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
            username = json["username"]
            adaccount: AdAccount = AdAccount(
                id=id,
                channel=ChannelType.instagram_media,
                account_id=id,
                name=username,
                img="instagram-icon",
            )
            adaccounts.append(adaccount)

    return adaccounts


@router.get("/fields", response_model=List[FieldOption])
def fields(
    default: bool = False, metrics: bool = False, dimensions: bool = False, media: bool = False
) -> List[FieldOption]:
    fields_options = None

    if media:
        if metrics:
            fields_options = instagram_media_metrics
        elif dimensions:
            fields_options = instagram_media_dimensions
        else:
            fields_options = instagram_media_metrics + instagram_media_dimensions
    else:
        if metrics:
            fields_options = instagram_account_metrics
        elif dimensions:
            fields_options = instagram_account_dimensions
        else:
            fields_options = instagram_account_metrics + instagram_account_dimensions

    if default:
        fields_options = [f for f in fields_options if f["default"]]

    return fields_options


@router.get("/delete")
def delete():
    return {"success": 200}


@router.get("/deauthorize")
def deauthorize():
    {"success": 200}
