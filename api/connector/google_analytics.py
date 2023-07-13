from api.config import Config
from api.core.auth import get_current_user
from api.core.static_data import ChannelType
from api.database.database import session
from api.utilities.google.auth import authorize, oauth2callback
from api.utilities.google.ga_runner import REFRESH_ERROR, create_client
from api.database.models import UserDB
from api.models.user import User
from api.models.google import GoogleQuery, GoogleQueryResults
from api.models.connector import AdAccount
from api.utilities.string import underscore_to_camel_case
from google.protobuf import json_format
from fastapi import Cookie

from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List

import json
import os
from pathlib import Path
from starlette.responses import RedirectResponse

from google.analytics.admin import AnalyticsAdminServiceClient
from google.analytics.admin_v1alpha.types import ListPropertiesRequest

# #  C:\repos\vizo-api\api\utilities\google\airpipe-378522-ed48c2ad4a0d.json


CLIENT_URL = Config.CLIENT_URL
GOOGLE_APPLICATION_CREDENTIALS_PATH = Config.GOOGLE_APPLICATION_CREDENTIALS_PATH


p = Path(r"api/utilities/google/airpipe-378522-ed48c2ad4a0d.json")
filename = str(p.absolute())
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = filename


router = APIRouter(prefix="/google-analytics")


@router.get("/ad_accounts", response_model=List[AdAccount])
def ad_accounts(token: str):
    current_user: User = get_current_user(token)
    client = AnalyticsAdminServiceClient()
    ad_accounts = []
    results = client.list_accounts()
    for account in results:
        id = account.name.replace("accounts/", "")
        properties = client.list_properties(ListPropertiesRequest(filter=f"parent:accounts/{id}", show_deleted=False))
        for property_ in properties:
            print(property_, "\n\n")
            property_id = property_.name.replace("properties/", "")
            name = property_.display_name.replace("display_name:", "")
            ad_accounts.append(
                AdAccount(
                    id=property_id, 
                    account_id=id,
                    channel=ChannelType.google_analytics,
                    name=name,
                    img="google-analytics-icon",
                )
            )
        

    #my property id - 365962034


    return ad_accounts


def handleGoogleTokenException(ex, current_user: User):
    error = str(ex)
    if REFRESH_ERROR in error:
        user = session.query(UserDB).filter(UserDB.email == current_user.email).first()
        user.google_access_token = None
        try:
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

        raise HTTPException(
            status_code=401,
            detail=f"Invalid refresh token.",
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error. {error}",
        )
