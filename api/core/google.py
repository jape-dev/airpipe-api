from api.config import Config
from api.models.user import User
from api.models.google import GoogleQuery
from api.database.models import UserDB
from api.utilities.string import underscore_to_camel_case
from api.database.database import session
from api.utilities.data import convert_metric

from datetime import datetime
from fastapi import HTTPException
import requests
from typing import List

REFRESH_ERROR = "Invalid refresh token"

GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
GOOGLE_ADS_DEVELOPER_TOKEN = Config.GOOGLE_ADS_DEVELOPER_TOKEN


def handleGoogleTokenException(ex, current_user: User):
    error = str(ex)
    if REFRESH_ERROR in error:
        try:
            user = (
                session.query(UserDB).filter(UserDB.email == current_user.email).first()
            )
            user.google_refresh_token = None
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


def build_google_query(
    fields: List[str], start_date: datetime, end_date: datetime
) -> str:
    fields = ",".join(fields)

    data_query = f"""
        SELECT {fields}
        FROM ad_group_ad
        WHERE segments.date BETWEEN "{start_date.strftime("%Y-%m-%d")}" AND "{end_date.strftime("%Y-%m-%d")}"
    """

    return data_query


def fetch_google_query(
    current_user: User, query: GoogleQuery, data_query: str
) -> List[object]:
    access_token = get_access_token(current_user.google_refresh_token)
    url = f"https://googleads.googleapis.com/v14/customers/{query.account_id}/googleAds:searchStream"
    body = {"query": data_query}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": GOOGLE_ADS_DEVELOPER_TOKEN,
    }
    response = requests.post(url, headers=headers, data=body)
    stream = response.json()

    data = []
    for batch in stream:
        try:
            results = batch["results"]
        except KeyError as e:
            print(e)
            print(batch)
            raise HTTPException(
                status_code=400,
                detail=f"Could not get data. {response.text}",
            )
        for row in results:
            data_row = {}
            for metric in query.metrics:
                metric_name = metric.replace("metrics.", "")
                metric_name = underscore_to_camel_case(metric_name)
                try:
                    data_row[metric] = convert_metric(
                        row["metrics"][metric_name], metric_name
                    )
                except BaseException as e:
                    print(row)
                    print("Error in metrics", e)
                    pass
            for dimension in query.dimensions:
                dimension_components = dimension.split(".")
                if dimension_components[0] == "segments":
                    if dimension_components[1] == "keyword":
                        try:
                            data_row[dimension] = row["segments"]["keyword"]["info"][
                                "text"
                            ]
                        except BaseException as e:
                            print(e)

                    else:
                        dimension_name = dimension.replace("segments.", "")
                        dimension_name = underscore_to_camel_case(dimension_name)
                        try:
                            data_row[dimension] = row["segments"][dimension_name]
                        except BaseException as e:
                            print(e)
                elif dimension_components[0] == "ad_group":
                    dimension_name = dimension.replace("ad_group.", "")
                    dimension_name = underscore_to_camel_case(dimension_name)
                    try:
                        data_row[dimension] = row["adGroup"][dimension_name]
                    except BaseException as e:
                        print(e)
                elif dimension_components[0] == "ad_group_ad":
                    dimension_name = dimension.replace("ad_group_ad.ad.", "")
                    dimension_name = underscore_to_camel_case(dimension_name)

                    try:
                        data_row[dimension] = row["adGroupAd"]["ad"][dimension_name]
                    except Exception as e:
                        print(e)
                elif dimension_components[0] == "campaign":
                    dimension_name = dimension.replace("campaign.", "")
                    dimension_name = underscore_to_camel_case(dimension_name)
                    try:
                        data_row[dimension] = row["campaign"][dimension_name]
                    except:
                        pass
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid dimension: {dimension}"
                    )

            data.append(data_row)

    return data


def get_access_token(refresh_token: str):
    url = "https://oauth2.googleapis.com/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not get access token")
    else:
        return response.json()["access_token"]
