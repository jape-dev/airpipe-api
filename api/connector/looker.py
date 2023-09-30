from fastapi import APIRouter, HTTPException
import sqlalchemy
from sqlalchemy.sql import text
from typing import List
from api.models.looker import LookerField, LookerDataRequest


from api.core.looker import get_looker_fields, map_postgres_type_to_looker_type
from api.database.database import engine


router = APIRouter(prefix="/looker")


@router.get("/table_schema", response_model=List[LookerField])
def table_schema(schema: str, name: str) -> List[LookerField]:
    connection = engine.connect()

    query = text(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = :name 
        --AND table_schema = :schema
        """
    )

    try:
        result = connection.execute(
            query,
            name=name,
            schema=schema,
        )
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)
    connection.close()

    schema = {}
    for row in result.all():
        field_name = row["column_name"]
        data_type = row["data_type"]
        schema[field_name] = data_type

    looker_schema = map_postgres_type_to_looker_type(schema)
    looker_fields = get_looker_fields(looker_schema)

    return looker_fields


@router.post("/table_data")
def table_data(request: LookerDataRequest):
    connection = engine.connect()

    columns = ", ".join(request.fields)
    query = f'SELECT {columns} FROM {request.db_schema}."{request.name}"'
    print("query", query)
    connection = engine.connect()
    try:
        results = connection.execute(query)
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)
    connection.close()

    data = []
    for row in results.all():
        print(row)
        values = {"values": list(row)}
        data.append(values)

    return data
