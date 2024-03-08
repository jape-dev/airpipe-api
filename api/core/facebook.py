from datetime import datetime, timedelta
import json
import time
from typing import List, Tuple
import requests
from fastapi import HTTPException

from api.models.facebook import FacebookQuery
from api.models.user import User


def get_date_range(query: FacebookQuery) -> Tuple[str, str]:
    """
    A function to get the date range based on the provided query.
    
    Args:
        query (FacebookQuery): The query object containing start and end dates.
        
    Returns:
        Tuple[str, str]: A tuple containing the start date and end date in the format "YYYY-MM-DD".

    """
    if query.start_date is None or query.end_date is None:
        # Defaults to a range of the last year if not specified
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
    else:
        start_datetime = datetime.fromtimestamp(query.start_date)
        end_datetime = datetime.fromtimestamp(query.end_date)
        start_date = start_datetime.strftime("%Y-%m-%d")
        end_date = end_datetime.strftime("%Y-%m-%d")

    return start_date, end_date


def get_date_range_increments(query):
    # Convert start and end dates from Unix timestamp to datetime objects
    if query.start_date is None or query.end_date is None:
        # Defaults to a range of the last year if not specified
        end_datetime = datetime.today()
        start_datetime = datetime.today() - timedelta(days=90)
    else:
        start_datetime = datetime.fromtimestamp(query.start_date)
        end_datetime = datetime.fromtimestamp(query.end_date)

    # Generate lists of 'since' and 'until' values in one-day increments
    since_dates = []
    until_dates = []

    current_date = start_datetime
    while current_date < end_datetime:
        since_dates.append(current_date.strftime("%Y-%m-%d"))
        next_day = current_date + timedelta(days=7)
        until_dates.append(next_day.strftime("%Y-%m-%d"))
        current_date = next_day

    return since_dates, until_dates


def process_data(data, query: FacebookQuery):
    """
    Process the given data according to the provided FacebookQuery object.

    Args:
        data: The data to be processed.
        query (FacebookQuery): The FacebookQuery object containing metrics and dimensions for processing.

    Returns:
        list: The processed data with modified metrics and dimensions.
    """
    for datum in data:
        # check if metric does not exist in the datum keys and set it to 0.
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

    # return data
                

def start_async_job(account_id, fields, since, until, access_token):
    """
    Start an asynchronous job to fetch insights data for a given time range.
    """
    url = f"https://graph.facebook.com/v17.0/{account_id}/insights"
    params = {
        'level': 'ad',
        'fields': fields,
        'time_range': json.dumps({'since': since, 'until': until}),
        'time_increment': 1,
        'access_token': access_token,
        'is_async': True
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        json_response = response.json()
        return json_response['report_run_id']
    else:
        print(response.text)
        raise HTTPException(status_code=response.status_code, detail="Failed to start async job: " + response.text)



def poll_async_job_status(report_run_id, access_token):
    """
    Poll the async job status until it is completed.
    """
    url = f"https://graph.facebook.com/v17.0/{report_run_id}"
    params = {'access_token': access_token}
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            json_response = response.json()
            status = json_response.get('async_status')
            if status == 'Job Completed':
                return True
            elif status in ['Job Failed', 'Job Skipped']:
                print("Job failed or skipped")
                return False
        else:
            print(response.text)
            return False
        time.sleep(10)  # Adjust the sleep time as necessary

def fetch_async_job_results(report_run_id, access_token):
    """
    Fetch the results of a completed asynchronous job.
    """
    url = f"https://graph.facebook.com/v17.0/{report_run_id}/insights"
    params = {'access_token': access_token}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(response.text)
        return []


def fetch_facebook_data(current_user: User, query: FacebookQuery) -> List[object]:

    fields = query.dimensions + query.metrics
    if "date" in fields:
        fields.remove("date")
    if "video_view" in fields or "post" in fields:
        fields.remove("video_view")
        fields.remove("post")
        fields.append("actions")

    fields = ",".join(fields)

    since_list, until_list = get_date_range_increments(query)
    
    all_data = []
    
    for since, until in zip(since_list, until_list):

        try:
            report_run_id = start_async_job(query.account_id, fields, since, until, current_user.facebook_access_token)
            if poll_async_job_status(report_run_id, current_user.facebook_access_token):
                data = fetch_async_job_results(report_run_id, current_user.facebook_access_token)
                print(data)
                process_data(data, query)
                all_data.extend(data)
            else:
                print("Async job failed or was skipped for the range:", since, until)
        except BaseException as e:
            print(f"Error starting async job for the range {since} to {until}: {e.detail}")
    
    
    return all_data