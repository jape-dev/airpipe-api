from fastapi import APIRouter, Request, HTTPException
from typing import List
import requests
from starlette.responses import RedirectResponse


from api.config import Config
from api.core.auth import get_current_user
from api.core.static_data import ChannelType
from api.core.google import get_access_token
from api.database.database import session
from api.utilities.google.auth import authorize, oauth2callback
from api.database.models import UserDB
from api.models.user import User
from api.models.connector import AdAccount


CLIENT_URL = Config.CLIENT_URL
GOOGLE_ADS_DEVELOPER_TOKEN = Config.GOOGLE_ADS_DEVELOPER_TOKEN

router = APIRouter(prefix="/google")


@router.get("/auth")
def auth(request: Request) -> RedirectResponse:
    token = request.query_params["token"]
    google_token = request.query_params["googleToken"]
    channel = request.query_params["channel"]
    channel_type = ChannelType[channel]
    auth_info = authorize(channel_type)
    passthrough_val = auth_info["passthrough_val"]
    url = auth_info["authorization_url"]
    response = RedirectResponse(url=url)
    response.set_cookie("token", token, httponly=True, samesite="none", secure=True)
    response.set_cookie(
        "google_token", google_token, httponly=True, samesite="none", secure=True
    )
    response.set_cookie(
        "passthrough_val", passthrough_val, httponly=True, samesite="none", secure=True
    )
    response.set_cookie("channel", channel, httponly=True, samesite="none", secure=True)

    return response


@router.get("/oauth2_callback")
def oauth2_callback(request: Request) -> RedirectResponse:
    google_token = request.cookies.get("google_token")
    user_token = request.cookies.get("token")
    passthrough_val = request.cookies.get("passthrough_val")
    channel = request.cookies.get("channel")
    state = request.query_params["state"]
    code = request.query_params["code"]
    channel_type = ChannelType[channel]

    token = oauth2callback(passthrough_val, state, code, google_token, channel_type)
    user: User = get_current_user(user_token)

    try:
        user = session.query(UserDB).filter(UserDB.email == user.email).first()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Could not save google access token to database. {e}",
        )

    if channel_type == ChannelType.google_analytics:
        user.google_analytics_refresh_token = token
    elif channel_type == ChannelType.sheets:
        user.google_sheets_refresh_token = token
    else:
        user.google_refresh_token = token

    try:
        session.add(user)
        session.commit()
    except Exception as e:
        print(e)

        raise HTTPException(
            status_code=400,
            detail=f"Could not save google access token to database. {e}",
        )
    finally:
        session.close()

    response = RedirectResponse(url=CLIENT_URL)
    response.delete_cookie("token")
    response.delete_cookie("google_token")
    response.delete_cookie("passthrough_val")

    return response


@router.get("/ad_accounts", response_model=List[AdAccount])
def ad_accounts(token: str):
    current_user: User = get_current_user(token)
    access_token = get_access_token(current_user.google_refresh_token)
    url = "https://googleads.googleapis.com/v14/customers:listAccessibleCustomers"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": GOOGLE_ADS_DEVELOPER_TOKEN,
    }
    response = requests.get(url, headers=headers)
    resource_names = response.json()["resourceNames"]

    ad_accounts = []
    for resource_name in resource_names:
        id = resource_name.replace("customers/", "")
        query = "SELECT customer_client.id, customer_client.descriptive_name, customer_client.client_customer FROM customer_client WHERE customer_client.manager = False "
        url = f"https://googleads.googleapis.com/v14/customers/{id}/googleAds:searchStream"
        body = {"query": query}
        response = requests.post(url, headers=headers, data=body)
        stream = response.json()

        for batch in stream:
            results = batch["results"]
            for result in results:
                customer = result["customerClient"]

                if "descriptiveName" not in customer:
                    name = "Google ads account"
                else:
                    name = customer["descriptiveName"]

                ad_accounts.append(
                    AdAccount(
                        id=id,
                        channel=ChannelType.google,
                        account_id=customer["id"],
                        name=name,
                        img="google-ads-icon",
                    )
                )
    return ad_accounts
