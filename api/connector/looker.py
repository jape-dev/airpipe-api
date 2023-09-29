from fastapi import APIRouter
from sqlalchemy import inspect
from sqlalchemy.sql import text


from api.core.looker import map_postgres_type_to_looker_type
from api.database.database import engine

router = APIRouter(prefix="/looker")


@router.get("/get_table_schema")
def get_table_schema(schema: str, name: str):
    connection = engine.connect()

    query = text(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = :name 
        --AND table_schema = :schema
        """
    )

    result = connection.execute(
        query,
        name=name,
        schema=schema,
    )

    schema = {}
    for row in result.all():
        field_name = row["column_name"]
        data_type = row["data_type"]
        schema[field_name] = data_type

    looker_schema = map_postgres_type_to_looker_type(schema)

    return looker_schema
