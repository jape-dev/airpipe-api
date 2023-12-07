from fastapi import APIRouter, HTTPException
import requests
from api.config import Config

router = APIRouter(prefix="/dataherald")

DATABASE_URL = Config.DATABASE_URL

@router.post("/connect_db", status_code=201)
def connect_db(db_schema: str, use_ssh:bool=False, alias:str="airpipe_db") -> str:
    request_body = {
        "alias": "alias",
        "use_ssh": use_ssh,
        "connection_uri": f"{DATABASE_URL}?options=-csearch_path%3D{db_schema}"
    }

    response = requests.post("https://dataherald.onrender.com/api/v1/database-connections", json=request_body)

    if response.status_code == 201:
        result = response.json()
        return result['id']
    else:
        raise HTTPException(
                    status_code=400, detail=f"Could not save access token to database. {response.json()}"
                )