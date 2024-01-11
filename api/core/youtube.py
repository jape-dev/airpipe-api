from api.config import Config
from api.models.user import User
from api.models.youtube import YoutubeQuery
from api.database.models import UserDB
from api.database.database import session
from api.core.google import get_access_token

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


def fetch_youtube_data(
    current_user: User, query: YoutubeQuery
) -> List[object]:
    access_token = get_access_token(current_user.youtube_refresh_token)
    url = f"https://youtubeanalytics.googleapis.com/v2/reports"
    print(query)
    params = {
        'ids': f'channel=={query.account_id}',
        'startDate': query.start_date.strftime("%Y-%m-%d"),
        'endDate': query.end_date.strftime("%Y-%m-%d"),
        'metrics': ','.join(query.metrics),
        'dimensions': ','.join(query.dimensions),
    }
    print(params)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": GOOGLE_ADS_DEVELOPER_TOKEN,
    }
    response = requests.get(url, headers=headers, params=params)
    data = []

    if response.status_code == 200:
        results = response.json()
        # Extract column names from the columnHeaders
        column_names = [header['name'] for header in results['columnHeaders']]

        # Iterate over each row in the 'rows' array
        for row in results['rows']:
            # Create a dictionary for each row
            row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
            # Append the dictionary to the parsed_data list
            data.append(row_dict)
    else:
        print(response.text)
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Could not get youtube data. {response.text}",
        )

    return data