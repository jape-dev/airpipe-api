from fastapi import APIRouter, HTTPException
import requests
from api.config import Config

from api.database.models import DataSourceDB, ViewDB
from api.database.database import session

router = APIRouter(prefix="/dataherald")

DATABASE_URL = Config.DATABASE_URL

@router.post("/connect_db", status_code=201)
def connect_db(table_id: int, db_schema: str, use_ssh:bool=False, data_source:bool=True) -> str:
    request_body = {
        "alias": "alias",
        "use_ssh": use_ssh,
        "connection_uri": f"{DATABASE_URL}?options=-csearch_path%3D{db_schema}"
    }

    response = requests.post("https://dataherald.onrender.com/api/v1/database-connections", json=request_body)

    if response.status_code == 201:
        result = response.json()

        # Save the connection to the database.
        try:
            if data_source:
                data_source = session.query(DataSourceDB).filter(DataSourceDB.id == table_id).first()
                data_source.dh_connection_id = result['id']
                session.add(data_source)
            else:
                view = session.query(ViewDB).filter(ViewDB.id == table_id).first()
                view.dh_connection_id = result['id']
                session.add(view)
            session.commit()
        except:
            raise HTTPException(
                status_code=400, detail=f"Could not save dh_connection_id to database. {response.json()}"
            )
        finally:
            session.close()
            session.remove()

        return result['id']
    else:
        raise HTTPException(
                    status_code=400, detail=f"Could not save access token to database. {response.json()}"
                )