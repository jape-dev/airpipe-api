from fastapi import APIRouter, Request, HTTPException
from typing import List
import requests
from starlette.responses import RedirectResponse


from api.config import Config
from api.core.auth import get_current_user
from api.core.data import add_data_source_row_to_db
from api.core.static_data import ChannelType, ReportType, google_metrics, google_dimensions, google_video_metrics, google_video_dimensions
from api.core.google import get_access_token
from api.database.database import session
from api.database.crud import get_user_by_email
from api.utilities.google.auth import authorize, oauth2callback
from api.database.models import UserDB, DataSourceDB
from api.models.user import User
from api.models.connector import AdAccount
from api.models.data import FieldOption


CLIENT_URL = Config.CLIENT_URL
GOOGLE_ADS_DEVELOPER_TOKEN = Config.GOOGLE_ADS_DEVELOPER_TOKEN
GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
AIRBYTE_WORKSPACE_ID = Config.AIRBYTE_WORKSPACE_ID
AIRBYTE_BASIC_TOKEN = Config.AIRBYTE_BASIC_TOKEN

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
    elif channel_type == ChannelType.youtube:
        user.youtube_refresh_token = token
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
        session.remove()

    redirect_client_url = f"{CLIENT_URL}/add-data-source/"
    response = RedirectResponse(url=redirect_client_url)
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
        query = "SELECT customer_client.id, customer_client.descriptive_name, customer_client.client_customer, customer_client.manager FROM customer_client WHERE customer_client.manager = False "
        url = f"https://googleads.googleapis.com/v14/customers/{id}/googleAds:searchStream"
        body = {"query": query}
        response = requests.post(url, headers=headers, data=body)
        stream = response.json()

        for batch in stream:
            try:
                results = batch["results"]
            except KeyError as e:

                error_status = batch['error']['status']

                if error_status == "PERMISSION_DENIED":
                    print(f"Permission denied error. {response.text}")
                    pass
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Could not get ad accounts. {response.text}",
                    )
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


@router.get("/fields", response_model=List[FieldOption])
def fields(
    default: bool = False, metrics: bool = False, dimensions: bool = False, report_type: ReportType = ReportType.google_standard
) -> List[FieldOption]:
    fields_options = None

    if report_type == ReportType.google_standard:
        if metrics:
            fields_options = google_metrics
        elif dimensions:
            fields_options = google_dimensions
        else:
            fields_options = google_metrics + google_dimensions
    elif report_type == ReportType.google_video:
        if metrics:
            fields_options = google_video_metrics
        elif dimensions:
            fields_options = google_video_dimensions
        else:
            fields_options = google_video_metrics + google_video_dimensions

    if default:
        fields_options = [f for f in fields_options if f["default"]]

    return fields_options


@router.post("/create_airbyte_source")
def create_airbyte_source(token: str, ad_account: AdAccount) -> DataSourceDB:
    current_user: User = get_current_user(token)
    access_token = get_access_token(current_user.google_refresh_token)

    url = "https://airpipe.network/v1/sources"

    payload = {
        "configuration": {
            "sourceType": "google-ads",
            "credentials": {
                "developer_token": GOOGLE_ADS_DEVELOPER_TOKEN,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": current_user.google_refresh_token,
                "access_token": access_token
            },
            "customer_status_filter": ["ENABLED"],
            "customer_id": ad_account.account_id
            },
        "name": ad_account.name,
        "workspaceId": AIRBYTE_WORKSPACE_ID
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {AIRBYTE_BASIC_TOKEN}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print(response.text)
        source_id = response.json()["sourceId"]
        user = get_user_by_email(current_user.email)
        data_source_row = add_data_source_row_to_db(user, ad_account, source_id)
    else:
        print(response.text)
        raise HTTPException(status_code=response.status_code, detail=f"Could not create Google Ads data source on AirByte. {response.text}")

    return data_source_row
