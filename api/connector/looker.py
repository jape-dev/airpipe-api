from fastapi import APIRouter, HTTPException
import sqlalchemy
from sqlalchemy.sql import text
from typing import List
from api.models.looker import LookerField, LookerDataRequest, LookerTable
from api.core.looker import get_looker_fields, map_postgres_type_to_looker_type
from api.database.database import engine
from api.database.crud import get_user_by_email
from api.database.crud import get_data_sources_by_user_id, get_views_by_user_id
from api.database.models import DataSourceDB, ViewDB
from api.utilities.data import get_channel_name_from_enum


router = APIRouter(prefix="/looker")


@router.get("/tables", response_model=List[LookerTable])
def tables(email: str) -> List[LookerTable]:
    db_user = get_user_by_email(email)
    data_sources: List[DataSourceDB] = get_data_sources_by_user_id(db_user.id)
    views: List[ViewDB] = get_views_by_user_id(db_user.id)

    looker_tables = []
    if data_sources:
        for data_source in data_sources:
            channel = get_channel_name_from_enum(data_source.channel)
            label = f"{channel} - {data_source.ad_account_id}"
            looker_tables.append(
                LookerTable(
                    db_schema=data_source.db_schema, name=data_source.name, label=label
                )
            )
    if views:
        for view in views:
            looker_tables.append(
                LookerTable(db_schema=view.db_schema, name=view.name, label=view.name)
            )

    return looker_tables


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
    connection = engine.connect()
    try:
        results = connection.execute(query)
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)
    connection.close()

    data = []
    for row in results.mappings().all():
        row_dict = dict(row)

        if "date" in row_dict:
            date = row_dict["date"]
            row_dict["date"] = date.replace("-", "")

        values = {"values": list(row_dict.values())}
        data.append(values)

    return data
