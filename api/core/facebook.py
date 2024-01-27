from datetime import datetime, timedelta
from typing import List
import requests
from fastapi import HTTPException

from api.models.facebook import FacebookQuery
from api.models.user import User


def fetch_facebook_data(current_user: User, query: FacebookQuery) -> List[object]:
    fields = query.dimensions + query.metrics
    if "date" in fields:
        fields.remove("date")
    if "video_view" in fields or "post" in fields:
        fields.remove("video_view")
        fields.remove("post")
        fields.append("actions")

    fields = ",".join(fields)

    if query.start_date is None or query.end_date is None:
        # today's date
        end_date = datetime.today().strftime("%Y-%m-%d")

        # today's date minus one year
        start_date = datetime.today() - timedelta(days=365)
        start_date = start_date.strftime("%Y-%m-%d")
    else:
        start_datetime = datetime.fromtimestamp(query.start_date)
        end_datetime = datetime.fromtimestamp(query.end_date)
        start_date = start_datetime.strftime("%Y-%m-%d")
        end_date = end_datetime.strftime("%Y-%m-%d")

    url = f"https://graph.facebook.com/v17.0/{query.account_id}/insights?level=ad&fields={fields}&time_range={{'since':'{start_date}','until':'{end_date}'}}&time_increment=1&access_token={current_user.facebook_access_token}"
    print(url)

    response = requests.get(url)
    if response.status_code != 200:
        print(response.text)
        raise HTTPException(status_code=400, detail="Facebook query failed")
    json = response.json()
    data = json["data"]
    print(data)

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

        for key, value in datum.items():
            # Check if the value is a list
            if isinstance(value, list):
                # Extract the video_view from the list
                video_view = next((item['value'] for item in value if item['action_type'] == 'video_view'), None)
                # Extract post shares from the list
                post_shares = next((item['value'] for item in value if item['action_type'] == 'post'), None)
                if video_view is not None:
                    if key != "actions":
                        datum[key] = video_view
                    else:
                        datum["video_view"] = video_view
                if post_shares is not None:
                    if key != "actions":
                        datum[key] = post_shares
                    else:
                        datum["post"] = post_shares
        
        # Remove the action key from each datum
        for datum in data:
            # Remove the action key from each datum
            if "actions" in datum:
                del datum["actions"]
    
    return data
