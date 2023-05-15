from api.models.data import TableColumns, CurrentResults, QueryResults, DataSource
from api.database.database import engine, session
from api.database.crud import get_user_by_email
from api.core.static_data import ChannelType, FieldType
from api.core.google import build_google_query, fetch_google_query
from api.core.facebook import fetch_facebook_data
from api.database.models import DataSourceDB
from api.database.crud import get_data_sources_by_user_id
from api.models.data import DataSourceInDB
from api.models.google import GoogleQuery
from api.models.facebook import FacebookQuery
from api.utilities.data import create_table_name


from fastapi import APIRouter, HTTPException, Body
import pandas as pd
import sqlalchemy
from typing import List

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
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)

    query_results = QueryResults(results=results.all())

    return query_results


@router.get("/table_results", response_model=CurrentResults, status_code=200)
def table_results(table_name: str):
    query = f'SELECT * FROM "{table_name}"'
    connection = engine.connect()
    try:
        results = connection.execute(query)
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)

    current_results = CurrentResults(name=table_name, results=results.all(), columns=list(results.keys()))

    return current_results


@router.post("/create_new_table")
def create_new_table(results: CurrentResults = Body(...)):
    df = pd.DataFrame(results.results, columns=results.columns)
    df = df.apply(pd.to_numeric, errors="ignore")
    df.to_sql(results.name, engine, if_exists="replace", index=False)

    return {"message": "success"}


@router.post("/add_data_source")
def add_data_source(data_source: DataSource = Body(...)) -> CurrentResults:
    # Reads data source
    account_id = data_source.adAccount.id
    metrics = [
        field.value for field in data_source.fields if field.type == FieldType.metric
    ]
    dimensions = [
        field.value for field in data_source.fields if field.type == FieldType.dimension
    ]
    fields = metrics + dimensions

    # Builds query depending on the channel type
    if data_source.adAccount.channel == ChannelType.google:

        data_query = build_google_query(fields=fields, start_date=data_source.start_date, end_date=data_source.end_date)
        query = GoogleQuery(
            account_id=account_id, metrics=metrics, dimensions=dimensions, start_date=data_source.start_date, end_date=data_source.end_date
        )
        data = fetch_google_query(
            current_user=data_source.user, query=query, data_query=data_query
        )
        fields = [f.split('.')[-1] for f in fields]

    elif data_source.adAccount.channel == ChannelType.facebook:
        query = FacebookQuery(
            account_id=account_id, metrics=metrics, dimensions=dimensions
        )
        data = fetch_facebook_data(current_user=data_source.user, query=query)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Channel type { data_source.adAccount.channel} not supported.",
        )

    db_user = get_user_by_email(data_source.user.email)

    table_name = create_table_name(data_source)

    # Saves data source to database.
    string_fields = ",".join(fields)
    data_source_row = DataSourceDB(
        user_id=db_user.id,
        name=data_source.name,
        table_name=table_name,
        fields=string_fields,
        channel=data_source.adAccount.channel,
        channel_img=data_source.adAccount.img,
        ad_account_id=data_source.adAccount.id,
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
            detail=f"Could not save data_source_row to databas3e. {e}",
        )

    results = CurrentResults(
        name=table_name,
        columns=fields,
        results=data,
    )

    return results


@router.get("/data_sources", response_model=List[DataSourceInDB], status_code=200)
def data_sources(email: str):
    db_user = get_user_by_email(email)
    data_sources = get_data_sources_by_user_id(db_user.id)

    data_sources_db = [
        DataSourceInDB(
            id=data_source.id,
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
