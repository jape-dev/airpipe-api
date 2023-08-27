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
