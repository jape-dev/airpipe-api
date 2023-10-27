from fastapi import APIRouter, HTTPException
import sqlalchemy
from typing import List

from api.models.data import (
    TableColumns,
    CurrentResults,
    QueryResults,
    DataSource,
    FieldOption,
)
from api.database.database import engine, session
from api.database.crud import get_user_by_email
from api.core.static_data import ChannelType, get_enum_member_by_value
from api.core.data import create_field_list, fetch_data, add_table_to_db
from api.models.data import DataSourceInDB
from api.database.models import DataSourceDB
from api.database.crud import get_data_sources_by_user_id
from api.utilities.data import (
    merge_objects,
    insert_alt_values,
    get_channel_img,
    object_list_to_df,
    pad_object_list,
)
from api.utilities.responses import SuccessResponse


router = APIRouter()


@router.get("/table_columns", response_model=TableColumns, status_code=200)
def get_table_columns(table_name: str):
    connection = engine.connect()
    result = connection.execute(f"SELECT * FROM {table_name} LIMIT 1")
    cols = [col for col in result.keys()]
    table_columns = TableColumns(name=table_name, columns=cols)

    return table_columns


@router.get("/run_query", response_model=QueryResults, status_code=200)
def run_query(query: str):
    connection = engine.connect()
    try:
        results = connection.execute(query)
        columns = list(results.keys())
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)

    query_results = QueryResults(columns=columns, results=results.all())

    return query_results


@router.get("/table_results", response_model=CurrentResults, status_code=200)
def table_results(schema: str, name: str):
    query = f'SELECT * FROM {schema}."{name}"'
    connection = engine.connect()
    try:
        results = connection.execute(query)
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)

    current_results = CurrentResults(
        name=f'{schema}."{name}"', results=results.all(), columns=list(results.keys())
    )

    return current_results


@router.post("/add_data_source", response_model=SuccessResponse, status_code=200)
def add_data_source(data_source: DataSource) -> SuccessResponse:
    # Reads data source

    data_list = fetch_data(data_source)
    data_list = [insert_alt_values(data, data_source.fields) for data in data_list]
    data = merge_objects(data_list)
    data = pad_object_list(data)
    df = object_list_to_df(data)

    db_user = get_user_by_email(data_source.user.email)
    name = data_source.name.replace(" ", "_")

    table_name = f"_{db_user.id}.{name}"
    db_schema = f"_{db_user.id}"

    # Saves table to the dataabase
    add_table_to_db(db_schema, name, df)

    columns, metrics, dimensions = create_field_list(
        data_source.fields, use_alt_value=True, split_value=True
    )
    channel_img = get_channel_img(data_source.fields)

    channel_type = get_enum_member_by_value(
        ChannelType, data_source.adAccounts[0].channel
    )

    # Saves data source to database.
    string_fields = ",".join(columns)
    data_source_row = DataSourceDB(
        user_id=db_user.id,
        db_schema=db_schema,
        name=name,
        table_name=table_name,
        fields=string_fields,
        channel=channel_type,
        channel_img=channel_img,
        ad_account_id=data_source.adAccounts[0].id,
        start_date=data_source.start_date,
        end_date=data_source.end_date,
    )

    try:
        session.add(data_source_row)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Could not save data_source_row to database. {e}",
        )

    return SuccessResponse(detail="Data written to db and data source record added.")


@router.get("/data_sources", response_model=List[DataSourceInDB], status_code=200)
def data_sources(email: str):
    db_user = get_user_by_email(email)
    data_sources = get_data_sources_by_user_id(db_user.id)

    data_sources_db = [
        DataSourceInDB(
            id=data_source.id,
            db_schema=data_source.db_schema,
            name=data_source.name,
            table_name=data_source.table_name,
            user_id=data_source.user_id,
            fields=data_source.fields,
            channel=data_source.channel,
            channel_img=data_source.channel_img,
            ad_account_id=data_source.ad_account_id,
            start_date=data_source.start_date,
            end_date=data_source.end_date,
        )
        for data_source in data_sources
    ]

    return data_sources_db


@router.get("/field_options", response_model=List[FieldOption])
def field_options(channel: ChannelType) -> List[FieldOption]:
    channel_type = get_enum_member_by_value(ChannelType, channel)
    return create_field_list(channel=channel_type)
