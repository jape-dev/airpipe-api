from fastapi import APIRouter, HTTPException
from typing import List
import os
from pathlib import Path
import requests


from api.config import Config
from api.core.auth import get_current_user
from api.core.google import get_access_token
from api.core.static_data import (
    ChannelType,
    youtube_metrics,
    youtube_dimensions,
)
from api.core.data import add_data_source_row_to_db
from api.database.crud import get_user_by_email
from api.database.database import session
from api.database.models import UserDB, DataSourceDB
from api.models.user import User
from api.models.data import FieldOption
from api.models.connector import AdAccount



REFRESH_ERROR = "Request had invalid authentication credentials"


CLIENT_URL = Config.CLIENT_URL
GOOGLE_APPLICATION_CREDENTIALS_PATH = Config.GOOGLE_APPLICATION_CREDENTIALS_PATH
GOOGLE_ADS_DEVELOPER_TOKEN = Config.GOOGLE_ADS_DEVELOPER_TOKEN
GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
AIRBYTE_WORKSPACE_ID = Config.AIRBYTE_WORKSPACE_ID
AIRBYTE_BASIC_TOKEN = Config.AIRBYTE_BASIC_TOKEN

# p = Path(r"api/utilities/google/airpipe-378522-ed48c2ad4a0d.json")
# filename = str(p.absolute())

filename = GOOGLE_APPLICATION_CREDENTIALS_PATH
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = filename

router = APIRouter(prefix="/youtube")


@router.get("/ad_accounts", response_model=List[AdAccount])
def ad_accounts(token: str):
    current_user: User = get_current_user(token)
    access_token = get_access_token(current_user.youtube_refresh_token)

    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        'part': 'snippet',
        'mine': 'true'
    }

    response = requests.get(url, headers=headers, params=params)

    print(response.json())

    ad_accounts = []
    if response.status_code == 200:
        results = response.json()
        try:
            for account in results["items"]:
                id = account["id"]
                name = account["snippet"]["title"]
                ad_accounts.append(
                    AdAccount(
                        id=id,
                        account_id=id,
                        channel=ChannelType.youtube,
                        name=name,
                        img="youtube-icon",
                    )
                )
        except KeyError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Could not get ad accounts. {e}",
            )
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Could not get ad accounts. {response.text}",
        )

    return ad_accounts


@router.get("/fields", response_model=List[FieldOption])
def fields(
    default: bool = False, metrics: bool = False, dimensions: bool = False
) -> List[FieldOption]:
    fields_options = None
    if metrics:
        fields_options = youtube_metrics
    elif dimensions:
        fields_options = youtube_dimensions
    else:
        fields_options = youtube_metrics + youtube_dimensions

    if default:
        fields_options = [f for f in fields_options if f["default"]]

    return fields_options


def handleGoogleTokenException(ex, current_user: User):
    error = str(ex)
    if REFRESH_ERROR in error:
        try:
            user = (
                session.query(UserDB).filter(UserDB.email == current_user.email).first()
            )
            user.google_analytics_refresh_token = None
            session.add(user)
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Could not save google access token to database. {e}",
            )
        finally:
            session.close()
            session.remove()

        raise HTTPException(
            status_code=401,
            detail=f"Invalid refresh token.",
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error. {error}",
        )

@router.post("/create_airbyte_source")
def create_airbyte_source(token: str, ad_account: AdAccount) -> DataSourceDB:
    current_user: User = get_current_user(token)

    url = "https://airpipe.network/v1/sources"

    payload = {
        "configuration": {
            "sourceType": "youtube-analytics",
            "credentials": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": current_user.youtube_refresh_token,
            }
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
        raise HTTPException(status_code=response.status_code, detail=f"Could not create YouTube data source on AirByte. {response.text}")

    return data_source_row