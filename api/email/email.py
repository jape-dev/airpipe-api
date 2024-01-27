import requests
from fastapi import HTTPException

from api.config import Config
from api.models.loops import Contact

LOOPS_API_KEY = Config.LOOPS_API_KEY


def add_contact_to_loops(contact: Contact):
    url = "https://app.loops.so/api/v1/contacts/create"
    headers = {
        "Authorization": f"Bearer {LOOPS_API_KEY}",
    }
    body = {
        "email": contact.email,
        "environment": contact.environment,
    }
    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        print(response.text)
        raise HTTPException(status_code=400, detail="Could not add contact to loops")

    return response


def send_remind_connect_event(contact: Contact):

    url = "https://app.loops.so/api/v1/events/send"

    payload = {
        "email": contact.email,
        "eventName": "remindConnect"
    }
    headers = {
        "Authorization": f"Bearer {LOOPS_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code != 200:
        print(response.text)
        raise HTTPException(status_code=400, detail="Could not send remind connect event")

    return response


def send_remind_data_source_event(contact: Contact):

    url = "https://app.loops.so/api/v1/events/send"

    payload = {
        "email": contact.email,
        "eventName": "remindDataSource"
    }
    headers = {
        "Authorization": f"Bearer {LOOPS_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code != 200:
        print(response.text)
        raise HTTPException(status_code=400, detail="Could not send remind connect event")

    return response


def send_added_data_source_event(contact: Contact):

    url = "https://app.loops.so/api/v1/events/send"

    payload = {
        "email": contact.email,
        "eventName": "addedDataSource"
    }
    headers = {
        "Authorization": f"Bearer {LOOPS_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code != 200:
        print(response.text)
        raise HTTPException(status_code=400, detail="Could not send add data source event")

    return response


