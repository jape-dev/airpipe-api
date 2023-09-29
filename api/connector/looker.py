from fastapi import APIRouter
from sqlalchemy.sql import text
from typing import List
from api.models.looker import LookerField


from api.core.looker import get_looker_fields, map_postgres_type_to_looker_type
from api.database.database import engine


router = APIRouter(prefix="/looker")


@router.get("/get_table_schema", response_model=List[LookerField])
def get_table_schema(schema: str, name: str) -> List[LookerField]:
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

    connection.close()

    schema = {}
    for row in result.all():
        field_name = row["column_name"]
        data_type = row["data_type"]
        schema[field_name] = data_type

    looker_schema = map_postgres_type_to_looker_type(schema)

    looker_fields = get_looker_fields(looker_schema)

    return looker_fields
