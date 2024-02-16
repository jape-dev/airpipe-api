from fastapi import APIRouter, HTTPException
import requests
from api.config import Config

from api.database.models import DataSourceDB, ViewDB
from api.database.database import session

router = APIRouter(prefix="/dataherald")

DATABASE_URL = Config.DATABASE_URL

@router.post("/connect_db", status_code=201)
def connect_db(table_id: int, db_schema: str, use_ssh:bool=False, data_source:bool=True) -> str:

    if data_source:
        table: DataSourceDB = session.query(DataSourceDB).filter(DataSourceDB.id == table_id).first()
    else:
        table: ViewDB = session.query(ViewDB).filter(ViewDB.id == table_id).first()

    request_body = {
        "alias": "alias",
        "use_ssh": use_ssh,
        "connection_uri": f"{DATABASE_URL}?options=-csearch_path%3D{db_schema}"
    }

    response = requests.post("https://dataherald.onrender.com/api/v1/database-connections", json=request_body)

    if response.status_code != 201:
        print(response.json())
        raise HTTPException(
            status_code=response.status_code, detail=f"Could not create dataherald database connection. {response.json()}"
        )

    result = response.json()
    connection_id = result['id']

    scan_request_body = {
        "db_connection_id": connection_id,
        "table_names": [table.name]
    }

    response = requests.post("https://dataherald.onrender.com/api/v1/table-descriptions/sync-schemas", json=scan_request_body)

    if response.status_code != 201:
        print(response.json())
        raise HTTPException(
            status_code=response.status_code, detail=f"Could not scan table. {response.json()}"
        )


    result = response.json()

    # add instrcutions
    instruction_one_request_body = {
        "db_connection_id": connection_id,
        "instruction":
            "Unless specified, give calculations to two decimal places.",
    }

    response = requests.post("https://dataherald.onrender.com/api/v1/instructions", json=instruction_one_request_body)

    if response.status_code != 201:
        print(response.json())
        raise HTTPException(
            status_code=response.status_code, detail=f"Could not add instruction 1 to database. {response.json()}"
        )

    instruction_two_request_body = {
        "db_connection_id": connection_id,
        "instruction":
            f"Only use the table: {table.name} to answer the question.",
    }

    response = requests.post("https://dataherald.onrender.com/api/v1/instructions", json=instruction_two_request_body)

    if response.status_code != 201: 
        print(response.json())
        raise HTTPException(
            status_code=response.status_code, detail=f"Could not add instruction 2 to database. {response.json()}"
        )

    try:
        table.dh_connection_id = connection_id
        session.add(table)
        session.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail=f"Could not save table to database. {e}"
        )
    finally:
        session.close()
        session.remove()


    return connection_id
