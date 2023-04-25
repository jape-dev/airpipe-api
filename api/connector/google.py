from api.config import Config
from api.core.auth import get_current_user
from api.database.database import session
from api.utilities.google.auth import authorize, oauth2callback
from api.utilities.google.ga_runner import REFRESH_ERROR, create_client
from api.database.models import UserDB
from api.models.user import User
from api.models.google import GoogleQuery, GoogleQueryResults
from api.models.connector import AdAccount
from google.protobuf import json_format

from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
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
        print(e)
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
    current_user: User = get_current_user(token)
    try:
        client = create_client(current_user.google_access_token)
        ga_service = client.get_service("GoogleAdsService")
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        for resource_name in accessible_customers.resource_names:
            id = resource_name.replace("customers/", "")
            query = "SELECT customer_client.id, customer_client.descriptive_name, customer_client.client_customer FROM customer_client"
            search_request = client.get_type("SearchGoogleAdsStreamRequest")
            search_request.customer_id = id
            search_request.query = query
            stream = ga_service.search_stream(search_request)
            ad_accounts = []
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
                            account_id=customer["id"],
                            name=name,
                            img="google-ads-icon",
                        )
                    )
        return ad_accounts
    except Exception as ex:
        handleGoogleTokenException(ex, current_user)


@router.post("/run_query", response_model=GoogleQueryResults)
def run_query(query: GoogleQuery, token: str):
    def underscore_to_camel_case(s):
        parts = s.split("_")
        return parts[0] + "".join(part.title() for part in parts[1:])

    current_user: User = get_current_user(token)

    fields = query.dimensions + query.metrics
    fields = ",".join(fields)

    start_datetime = datetime.fromtimestamp(query.start_date)
    end_datetime = datetime.fromtimestamp(query.end_date)
    start_date = start_datetime.strftime("%Y-%m-%d")
    end_date = end_datetime.strftime("%Y-%m-%d")

    try:
        client = create_client(current_user.google_access_token)
        ga_service = client.get_service("GoogleAdsService")

        data_query = f"""
            SELECT {fields}
            FROM ad_group_ad
            WHERE segments.date BETWEEN "{start_date}" AND "{end_date}"
        """

        search_request = client.get_type("SearchGoogleAdsStreamRequest")
        search_request.customer_id = query.account_id
        search_request.query = data_query
        stream = ga_service.search_stream(search_request)
    except Exception as ex:
        handleGoogleTokenException(ex, current_user)

    data = []
    for batch in stream:
        for result in batch.results:
            json_str = json_format.MessageToJson(result._pb)
            row = json.loads(json_str)
            data_row = {}
            for metric in query.metrics:
                metric_name = metric.replace("metrics.", "")
                metric_name = underscore_to_camel_case(metric_name)
                try:
                    data_row[metric.replace("metrics.", "")] = row["metrics"][
                        metric_name
                    ]
                except BaseException as e:
                    print(e)
                    pass
            for dimension in query.dimensions:
                dimension_components = dimension.split(".")
                if dimension_components[0] == "segments":
                    if dimension_components[1] == "keyword":
                        try:
                            data_row["keyword_text"] = row["segments"]["keyword"][
                                "info"
                            ]["text"]
                        except BaseException as e:
                            print(e)

                    else:
                        dimension_name = dimension.replace("segments.", "")
                        dimension_name = underscore_to_camel_case(dimension_name)
                        try:
                            data_row[dimension.replace("segments.", "")] = row[
                                "segments"
                            ][dimension_name]
                        except BaseException as e:
                            print(e)
                elif dimension_components[0] == "ad_group":
                    dimension_name = dimension.replace("ad_group.", "")
                    dimension_name = underscore_to_camel_case(dimension_name)
                    try:
                        data_row[dimension.replace("ad_group.", "")] = row["ad_group"][
                            dimension_name
                        ]
                    except BaseException as e:
                        print(e)
                elif dimension_components[0] == "campaign":
                    dimension_name = dimension.replace("campaign.", "")
                    dimension_name = underscore_to_camel_case(dimension_name)
                    try:
                        data_row[dimension.replace("campaign.", "")] = row["campaign"][
                            dimension_name
                        ]
                    except:
                        pass
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid dimension: {dimension}"
                    )

            data.append(data_row)
    return GoogleQueryResults(results=data)


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
