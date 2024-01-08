from datetime import datetime, timedelta
from typing import List
import requests
from fastapi import HTTPException

from api.models.instagram import InstagramQuery
from api.models.user import User


def fetch_instagram_data(current_user: User, query: InstagramQuery) -> List[object]:
    metrics = ','.join(query.metrics)
    if "date" in query.dimensions:
        query.dimensions.remove("date")
    dimensions = ','.join(query.dimensions)


    if query.start_date is None or query.end_date is None:
        # today's date
        end_date = datetime.today().strftime("%Y-%m-%d")

        # today's date minus one year
        start_date = datetime.today() - timedelta(days=30)
        start_date = start_date.strftime("%Y-%m-%d")
    else:
        start_datetime = datetime.fromtimestamp(query.start_date)
        end_datetime = datetime.fromtimestamp(query.end_date)
        start_date = start_datetime.strftime("%Y-%m-%d")
        end_date = end_datetime.strftime("%Y-%m-%d")

    url = f"https://graph.facebook.com/v18.0/{query.account_id}/insights?metric={metrics}&breakdown={dimensions}&period={query.period}&since={start_date}&until={end_date}&access_token={current_user.instagram_access_token}"
    print(url)

    response = requests.get(url)
    if response.status_code != 200:
        print(response.text)
        raise HTTPException(status_code=response.status_code, detail="Instagram query failed: " + response.text)
    json = response.json()
    data = json["data"]

    parsed_data = []
    for datum in data:
        name = datum["name"]
        for value in datum["values"]:
            date = datetime.strptime(value['end_time'], "%Y-%m-%dT%H:%M:%S%z").date()
            parsed_data.append({name: value['value'], "date": date})

    return parsed_data
