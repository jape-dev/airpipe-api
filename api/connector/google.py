import json
from google.protobuf import json_format
from fastapi import APIRouter, Request, HTTPException
from typing import List
from starlette.responses import RedirectResponse


from api.config import Config
from api.core.auth import get_current_user
from api.core.static_data import ChannelType
from api.database.database import session
from api.utilities.google.auth import authorize, oauth2callback
from api.utilities.google.ga_runner import REFRESH_ERROR, create_client
from api.database.models import UserDB
from api.models.user import User
from api.models.connector import AdAccount


CLIENT_URL = Config.CLIENT_URL

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
    token = request.cookies.get("token")
    passthrough_val = request.cookies.get("passthrough_val")
    channel = request.cookies.get("channel")
    state = request.query_params["state"]
    code = request.query_params["code"]
    channel_type = ChannelType[channel]

    access_token = oauth2callback(
        passthrough_val, state, code, google_token, channel_type
    )
    user: User = get_current_user(token)

    try:
        session.connection(execution_options={None: "public"})
        user = session.query(UserDB).filter(UserDB.email == user.email).first()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Could not save google access token to database. {e}",
        )

    if channel_type == ChannelType.google_analytics:
        user.google_analytics_access_token = access_token
    else:
        user.google_access_token = google_token

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
    try:
        client = create_client(current_user.google_access_token)
        ga_service = client.get_service("GoogleAdsService")
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        ad_accounts = []
        for resource_name in accessible_customers.resource_names:
            id = resource_name.replace("customers/", "")
            query = "SELECT customer_client.id, customer_client.descriptive_name, customer_client.client_customer FROM customer_client WHERE customer_client.manager = False "
            search_request = client.get_type("SearchGoogleAdsStreamRequest")
            search_request.customer_id = id
            search_request.query = query
            stream = ga_service.search_stream(search_request)
            for batch in stream:
                for result in batch.results:
                    json_str = json_format.MessageToJson(result._pb)
                    row = json.loads(json_str)
                    customer = row["customerClient"]

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
    except Exception as ex:
        handleGoogleTokenException(ex, current_user)


def handleGoogleTokenException(ex, current_user: User):
    error = str(ex)
    if REFRESH_ERROR in error:

        try:
            user = (
                session.query(UserDB).filter(UserDB.email == current_user.email).first()
            )
            user.google_access_token = None
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
