from datetime import datetime, timedelta
from typing import List
import requests
from fastapi import HTTPException

from api.core.static_data import ChannelType
from api.models.instagram import InstagramQuery
from api.models.user import User


def fetch_instagram_data(current_user: User, query: InstagramQuery) -> List[object]:
    metrics = ','.join(query.metrics)
    dimension = query.dimensions
    if "date" in dimension:
        dimension.remove("date")
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


    parsed_data = []
    if query.channel == ChannelType.instagram_account:
        url = f"https://graph.facebook.com/v18.0/{query.account_id}?fields={dimensions}&access_token={current_user.instagram_access_token}"
        response = requests.get(url)
        if response.status_code != 200:
            print(response.text)
            raise HTTPException(status_code=response.status_code, detail="Instagram query failed in getting account data: " + response.text)
        account_json = response.json()
        metric_type = "time_series" if "date" in query.dimensions else "total_value"
        if metric_type == "total_value":
            metrics = [m for m in query.metrics if m not in ["email_contacts", "follower_count", "get_directions_clicks", "phone_call_clicks", "website_clicks", "text_message_clicks"]]
            metrics = ','.join(metrics)

        url = f"https://graph.facebook.com/v18.0/{query.account_id}/insights?metric={metrics}&period={query.period}&metric_type={metric_type}&since={start_date}&until={end_date}&access_token={current_user.instagram_access_token}"

        response = requests.get(url)
        if response.status_code != 200:
            print(response.text)
            raise HTTPException(status_code=response.status_code, detail="Instagram query failed in getting account data: " + response.text)
        json = response.json()
        data = json["data"]
        row = {}
        if metric_type == "time_series":
            for datum in data:
                name = datum["name"]
                for value in datum["values"]:
                    for dimension in query.dimensions:
                        try:
                            row[dimension] = account_json[dimension]
                        except KeyError:
                            pass
                    date = datetime.strptime(value['end_time'], "%Y-%m-%dT%H:%M:%S%z").date()
                    row[name] = value['value']
                    row["date"] = date
                    parsed_data.append(row)
        else:
            for datum in data:
                for dimension in query.dimensions:
                    try:
                        row[dimension] = account_json[dimension]
                    except KeyError:
                        pass
                name = datum["name"]
                row[name] = datum["total_value"]["value"]
            parsed_data.append(row)

    else:
        url = f"https://graph.facebook.com/v18.0/{query.account_id}?fields=media&access_token={current_user.instagram_access_token}"
        response = requests.get(url)
        if response.status_code != 200:
            print(response.text)
            raise HTTPException(status_code=response.status_code, detail="Instagram query failed in getting media ids: " + response.text)
        json = response.json()
        data = json["media"]["data"]

        media_ids = [media["id"] for media in data]

        for id in media_ids:
            url = f"https://graph.facebook.com/v18.0/{id}?fields=timestamp,media_type,media_product_type,{dimensions}&access_token={current_user.instagram_access_token}"
            response = requests.get(url)
            if response.status_code != 200:
                print(response.text)
                raise HTTPException(status_code=response.status_code, detail="Instagram query failed in getting media timestamp: " + response.text)
            json = response.json()
            timestamp = json["timestamp"]
            media_type = json["media_type"]
            media_product_type = json["media_product_type"]

            if media_type == "IMAGE" or media_type == "CAROUSEL_ALBUM":
                metrics = query.metrics
                items_to_remove = ["plays", "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"]
                metrics = [item for item in metrics if item not in items_to_remove]
                metrics = ','.join(metrics)
            elif media_type == "VIDEO" and media_product_type != "REELS":
                metrics = query.metrics
                items_to_remove = ["ig_reels_video_view_total_time", "ig_reels_avg_watch_time"]
                metrics = [item for item in metrics if item not in items_to_remove]
                metrics = ','.join(metrics)

            row = {}
            for dimension in query.dimensions:
                if dimension == "date":
                    row[dimension] = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z").date()
                elif dimension == "owner":
                    row[dimension] = json["owner"]["id"]
                else:
                    try:
                        row[dimension] = json[dimension]
                    except KeyError:
                        print("Dimension not foundin json " + dimension)
                        print(json)
                        pass

            url = f"https://graph.facebook.com/v18.0/{id}/insights?metric={metrics}&since={start_date}&until={end_date}&access_token={current_user.instagram_access_token}"

            response = requests.get(url)
            if response.status_code != 200:
                print(response.text)
                raise HTTPException(status_code=response.status_code, detail="Instagram query failed in getting media data: " + response.text)
            json = response.json()
            data = json["data"]

            for datum in data:
                name = datum["name"]
                for value in datum["values"]:
                    row[name] = value['value']
            parsed_data.append(row)

    return parsed_data
