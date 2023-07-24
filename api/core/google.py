from api.models.user import User
from api.models.google import GoogleQuery
from api.database.models import UserDB
from api.utilities.google.ga_runner import REFRESH_ERROR, create_client
from api.utilities.string import underscore_to_camel_case
from api.database.database import session


from fastapi import HTTPException
from google.protobuf import json_format
import json
from typing import List, Optional


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


def build_google_query(fields: List[str], start_date: str, end_date: str) -> str:
    fields = ",".join(fields)

    data_query = f"""
        SELECT {fields}
        FROM ad_group_ad
        WHERE segments.date BETWEEN "{start_date}" AND "{end_date}"
    """

    return data_query


def fetch_google_query(
    current_user: User, query: GoogleQuery, data_query: str
) -> List[object]:
    try:
        client = create_client(current_user.google_access_token)
        ga_service = client.get_service("GoogleAdsService")
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
                    data_row[metric] = row["metrics"][metric_name]
                except BaseException as e:
                    print(e)
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


def join_data_on_date():
    pass
