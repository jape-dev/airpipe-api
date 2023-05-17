from api.config import Config

from api.models.connector import AdAccount
from api.core.static_data import ChannelType
from api.models.user import User
from api.models.facebook import FacebookQuery, FacebookQueryResults
from api.core.auth import get_current_user
from api.database.database import session
from api.database.models import UserDB

from datetime import datetime
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

    redirect_uri = f"https://api-airpipe.com/connector/facebook/login/"
    auth_url = f"https://graph.facebook.com/v15.0/oauth/access_token?client_id={app_id}&redirect_uri={redirect_uri}&code={code}&client_secret={FB_CLIENT_SECRET}"

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

    user = session.query(UserDB).filter(UserDB.email == user.email).first()
    user.facebook_access_token = access_token
    try:
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

    redirect_client_url = f"{CLIENT_URL}/add-data/"

    return RedirectResponse(url=redirect_client_url)


@router.get("/ad_accounts", response_model=List[AdAccount])
def ad_accounts(token: str):
    current_user: User = get_current_user(token)
    adaccounts = []

    url = f"https://graph.facebook.com/v15.0/me?fields=adaccounts&access_token={current_user.facebook_access_token}"
    response = requests.get(url)
    json = response.json()
    accounts = json["adaccounts"]["data"]

    for account in accounts:
        id = account["id"]
        account_id = account["account_id"]
        url = f"https://graph.facebook.com/v15.0/{id}?fields=name&access_token={current_user.facebook_access_token}"
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


@router.post("/run_query", response_model=FacebookQueryResults)
def run_query(query: FacebookQuery, token: str):
    current_user: User = get_current_user(token)

    fields = query.dimensions + query.metrics
    if "date" in fields:
        fields.remove("date")
    fields = ",".join(fields)

    start_datetime = datetime.fromtimestamp(query.start_date)
    end_datetime = datetime.fromtimestamp(query.end_date)
    start_date = start_datetime.strftime("%Y-%m-%d")
    end_date = end_datetime.strftime("%Y-%m-%d")

    url = f"https://graph.facebook.com/v15.0/{query.account_id}/insights?level=ad&fields={fields}&time_range={{'since':'{start_date}','until':'{end_date}'}}&time_increment=1&access_token={current_user.facebook_access_token}"

    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Facebook query failed")
    json = response.json()
    data = json["data"]

    for datum in data:
        # check if metric doe snot exist in the datum keys and set it to 0.
        for metric in query.metrics:
            if metric not in datum.keys():
                datum[metric] = 0

        if datum["date_start"] == datum["date_stop"]:
            datum["date"] = datum["date_start"]
            del datum["date_start"]
            del datum["date_stop"]

            if "date" not in query.dimensions:
                del datum["date"]

    return FacebookQueryResults(results=data)
