from api.config import Config

from api.models.connector import AdAccount
from api.core.static_data import ChannelType, facebook_metrics, facebook_dimensions
from api.config import Config
from api.models.user import User
from api.core.auth import get_current_user
from api.database.database import session
from api.database.models import UserDB, DataSourceDB
from api.database.crud import get_user_by_email, get_data_source_by_airbyte_source_id
from api.models.data import FieldOption

from fastapi import APIRouter, Request, HTTPException
import requests
from starlette.responses import RedirectResponse
from typing import List, Optional

POSTGRES_HOST = Config.POSTGRES_HOST
POSTGRES_PASSWORD = Config.POSTGRES_PASSWORD
POSTGRES_USERNAME = Config.POSTGRES_USERNAME
POSTGRES_DB_NAME = Config.POSTGRES_DB_NAME
AIRBYTE_WORKSPACE_ID = Config.AIRBYTE_WORKSPACE_ID
AIRBYTE_BASIC_TOKEN = Config.AIRBYTE_BASIC_TOKEN

router = APIRouter(prefix="/airbyte")

@router.post("/create_postgres_destination")
def create_postgres_destination(token: str) -> UserDB:    
    current_user: User = get_current_user(token)
    user: UserDB = get_user_by_email(current_user.email)
    db_schema = f"_{user.id}"
    destination_name = f"postgres-{user.id}"

    url = "https://airpipe.network/v1/destinations"
    
    payload = {
        "configuration": {
                "destinationType": "postgres",
                "port": 5432,
                "schema": db_schema,
                "ssl_mode": {
                "mode": "allow"
            },
            "tunnel_method": {
            "tunnel_method": "NO_TUNNEL"
            },
            "host": POSTGRES_HOST,
            "database": POSTGRES_DB_NAME,
            "username": POSTGRES_USERNAME,
            "password": POSTGRES_PASSWORD
        },
        "name": destination_name,
        "workspaceId": AIRBYTE_WORKSPACE_ID
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {AIRBYTE_BASIC_TOKEN}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        destination_id = response.json()['destinationId']
        user.airbyte_destination_id = destination_id
        session.add(user)
        session.commit()
    else:
        print(response.text)
        raise HTTPException(status_code=response.status_code, detail=f"Could not create Postgres destination on Airbyte. {response.text}")

    return user


@router.post("/create_connection")
def create_connection(token: str, stream_name, source_id: str, destination_id: Optional[str] = None) -> DataSourceDB:
    current_user: User = get_current_user(token)
    user: UserDB = get_user_by_email(current_user.email)
    # Get the data source by the source_id
    data_source = get_data_source_by_airbyte_source_id(source_id)

    url = "https://airpipe.network/v1/connections"

    if not destination_id:
        destination_id = user.airbyte_destination_id

    payload = {
        "configurations": {
            "streams": [
            {
                "name": stream_name,
                "syncMode": "incremental_append"
            }
            ]
        },
        "schedule": {
            "scheduleType": "cron",
            "cronExpression": "0 0 3 * * ? *"
        },
        "dataResidency": "auto",
        "namespaceDefinition": "destination",
        "namespaceFormat": None,
        "nonBreakingSchemaUpdatesBehavior": "ignore",
        "sourceId": source_id,
        "destinationId": destination_id,
        "prefix": data_source.channel
    }


    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {AIRBYTE_BASIC_TOKEN}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        connection_id = response.json()['connectionId']
        data_source.airbyte_connection_id = connection_id
        session.add(data_source)
        session.commit()
    else:
        print(response.text)
        raise HTTPException(status_code=response.status_code, detail=f"Could not create Postgres destination on Airbyte. {response.text}")

    return data_source




    
    

