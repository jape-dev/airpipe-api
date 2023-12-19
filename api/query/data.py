from fastapi import APIRouter, HTTPException
import sqlalchemy
from typing import List, Optional
import pandas as pd

from api.models.data import (
    TableColumns,
    CurrentResults,
    QueryResults,
    DataSource,
    FieldOption,
    FieldOptionWithDataSourceId,
    Table
)
from api.database.database import engine, session
from api.database.crud import get_user_by_email
from api.core.static_data import ChannelType, get_enum_member_by_value
from api.core.data import (
    create_field_list,
    fetch_data,
    add_table_to_db,
    all_fields,
    build_blend_query,
    airpipe_field_option
)
from api.models.data import DataSourceInDB, JoinCondition, View, ViewInDB
from api.models.user import User
from api.database.models import DataSourceDB, ViewDB, JoinConditionDB
from api.database.crud import get_data_sources_by_user_id, get_views_by_user_id
from api.utilities.data import (
    insert_alt_values,
    get_channel_img,
    get_channel_name_from_enum
)
from api.utilities.responses import SuccessResponse
from pydantic import Field
from datetime import datetime
from api.core.auth import get_current_user

router = APIRouter()


@router.get("/table_columns", response_model=TableColumns, status_code=200)
def get_table_columns(token: str, table_name: str):
    get_current_user(token)
    connection = engine.connect()
    result = connection.execute(f"SELECT * FROM {table_name} LIMIT 1")
    cols = [col for col in result.keys()]
    table_columns = TableColumns(name=table_name, columns=cols)

    return table_columns


@router.post(
    "/data_source_field_options", response_model=List[FieldOption], status_code=200
)
def data_source_field_options(data_source: DataSourceInDB) -> List[FieldOption]:
    source_fields = data_source.fields.split(",")
    selected_fields = [
        field for field in all_fields if field.alt_value in source_fields
    ]

    return selected_fields


@router.post("/field_options", response_model=List[FieldOption], status_code=200)
def field_options(fields: List[str]) -> List[FieldOption]:

    fields_list = [
        next((field for field in all_fields if field.alt_value == field_name), airpipe_field_option(field_name))
        for field_name in fields
    ]
    
    return fields_list

@router.get("/channel_field_options", response_model=List[FieldOption])
def channel_field_options(channel: ChannelType, token: str) -> List[FieldOption]:
    # current_user: User = get_current_user(token) TODO: change auth set-up as this is clashing with ad_accounts
    channel_type = get_enum_member_by_value(ChannelType, channel)
    fields, metrics, dimensions = create_field_list(all_fields, channel=channel_type, use_alt_value=True)
    field_options = [
        next((field for field in all_fields if field.alt_value == field_name), airpipe_field_option(field_name))
        for field_name in fields
    ]
    return field_options



@router.get("/run_query", response_model=QueryResults, status_code=200)
def run_query(token: str, query: str):
    get_current_user(token)
    connection = engine.connect()
    try:
        results = connection.execute(query)
        columns = list(results.keys())
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)
    finally:
        connection.close()

    query_results = QueryResults(columns=columns, results=results.all())

    return query_results


@router.get("/table_results", response_model=CurrentResults, status_code=200)
def table_results(
    token: str,
    schema: str,
    name: str,
    date_column: Optional[str] = None,
    start_date: datetime = None,
    end_date: datetime = None,
):
    get_current_user(token)
    query = f'SELECT * FROM {schema}."{name}" '
    if date_column is not None and start_date is not None and end_date is not None:
        query += f"WHERE {date_column} BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'"
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
    df = pd.DataFrame(data_list[0])

    # Convert the DataFrame numerica values to numeric
    df = df.apply(pd.to_numeric, errors="ignore")

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
def data_sources(token: str):
    current_user: User = get_current_user(token)
    db_user = get_user_by_email(current_user.email)
    data_sources: List[DataSourceDB] = get_data_sources_by_user_id(db_user.id)

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


@router.get("/views", response_model=List[ViewInDB])
def views(token: str):
    current_user: User = get_current_user(token)
    db_user = get_user_by_email(current_user.email)
    views = get_views_by_user_id(db_user.id)
    views_db = [
        ViewInDB(
            id=view.id,
            user_id=view.user_id,
            db_schema=view.db_schema,
            name=view.name,
            table_name=view.table_name,
            fields=view.fields,
            start_date=view.start_date,
            end_date=view.end_date,
        )
        for view in views
    ]

    return views_db


@router.get("/tables", response_model=List[Table])
def tables(token: str) -> List[Table]:
    current_user: User = get_current_user(token)
    db_user = get_user_by_email(current_user.email)
    data_sources: List[DataSourceDB] = get_data_sources_by_user_id(db_user.id)
    views: List[ViewDB] = get_views_by_user_id(db_user.id)
    tables = []

    if data_sources:
        for data_source in data_sources:
            channel = get_channel_name_from_enum(data_source.channel)
            label = f"{channel} - {data_source.ad_account_id}"
            tables.append(
                Table(
                    id=data_source.id,
                    user_id=data_source.user_id,
                    db_schema=data_source.db_schema,
                    name=data_source.name,
                    table_name=data_source.table_name,
                    label=label,
                    channel=data_source.channel, 
                    channel_img=data_source.channel_img,
                    ad_account_id=data_source.ad_account_id,
                    fields=data_source.fields,
                    start_date=data_source.start_date,
                    end_date=data_source.end_date
                    )
                )
    if views:
        for view in views:
            tables.append(
                Table(id=view.id,
                      user_id=view.user_id,
                      db_schema=view.db_schema,
                      name=view.name,
                      table_name=view.table_name,
                      label=view.name,
                      fields=view.fields,
                      start_date=view.start_date,
                      end_date=view.end_date
                      )
                )

    return tables


@router.post("/create_blend", response_model=QueryResults)
def create_blend(
    token: str,
    fields: List[FieldOptionWithDataSourceId],
    join_conditions: List[JoinCondition],
    left_data_source: DataSourceInDB,
    right_data_source: DataSourceInDB,
    date_column: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    current_user: User = get_current_user(token)
    query = build_blend_query(
        fields=fields,
        join_conditions=join_conditions,
        left_data_source=left_data_source,
        right_data_source=right_data_source,
        date_column=date_column,
        start_date=start_date,
        end_date=end_date,
    )

    connection = engine.connect()
    try:
        results = connection.execute(query)
        columns = list(results.keys())
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)
    finally:
        connection.close()

    query_results = QueryResults(columns=columns, results=results.all())

    return query_results


@router.post("/save_view", response_model=ViewInDB)
def save_view(view: View, token: str) -> ViewInDB:
    current_user: User = get_current_user(token)
    db_user = get_user_by_email(current_user.email)
    name = view.name.replace(" ", "-").lower()

    table_name = f"_{db_user.id}.{name}"
    db_schema = f"_{db_user.id}"

    columns, metrics, dimensions = create_field_list(
        view.fields, use_alt_value=True, split_value=True
    )

    view_db = ViewDB(
        user_id=db_user.id,
        name=name,
        db_schema=db_schema,
        table_name=table_name,
        fields=",".join(columns),
        start_date=view.start_date,
        end_date=view.end_date,
    )

    try:
        session.add(view_db)
        session.flush()  # Flush the changes to the database to get the id
        session.commit()
        view_in_db = ViewInDB.from_orm(view_db)
    except Exception as e:
        print(e)
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Could not save view to database. {e}",
        )
    finally:
        session.close()

    if view.join_conditions:
        for condtion_id, condition in enumerate(view.join_conditions):
            join_condition = JoinConditionDB(
                condition_id=condtion_id,
                view_id=view_db.id,
                left_field=condition.left_field.alt_value,
                right_field=condition.right_field.alt_value,
                join_type=condition.join_type.value,
                left_data_source_id=condition.left_data_source_id,
                right_data_source_id=condition.right_data_source_id,
            )
            try:
                session.add(join_condition)
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not save join condition to database. {e}",
                )

    session.close()

    return view_in_db


@router.post("/save_table", response_model=SuccessResponse)
def save_table(token: str, results: CurrentResults, schema: str) -> SuccessResponse:
    get_current_user(token)
    df = pd.DataFrame(results.results, columns=results.columns)
    # Filter on date range here. Or ideally filter on dates when pulling from SQL.

    try:
        add_table_to_db(schema, results.name, df)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail=f"Could not save table to database. {e}",
        )

    return SuccessResponse(success=True)
