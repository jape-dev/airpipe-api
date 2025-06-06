from datetime import datetime, timedelta
from fastapi import HTTPException
import pandas as pd
from typing import List, Optional
import uuid

from api.core.google import build_google_query, fetch_google_data, build_google_video_query
from api.core.facebook import fetch_facebook_data
from api.core.instagram import fetch_instagram_data
from api.core.youtube import fetch_youtube_data
from api.database.database import engine, session
from api.models.data import (
    FieldOption,
    DataSource,
    JoinCondition,
    DataSourceInDB,
    FieldOptionWithDataSourceId,
    AdAccount
)
from api.database.models import DataSourceDB, UserDB
from api.models.google import GoogleQuery
from api.models.facebook import FacebookQuery
from api.models.youtube import YoutubeQuery
from api.models.instagram import InstagramQuery
from api.core.static_data import (
    FieldType,
    ChannelType,
    google_metrics,
    google_dimensions,
    google_video_metrics,
    google_video_dimensions,
    google_analytics_metrics,
    google_analytics_dimensions,
    facebook_metrics,
    facebook_dimensions,
    youtube_metrics,
    youtube_dimensions,
    instagram_account_metrics,
    instagram_account_dimensions,
    instagram_media_metrics,
    instagram_media_dimensions,
)
from api.core.google_analytics import fetch_google_analytics_data
from api.models.google_analytics import GoogleAnalyticsQuery


all_fields: List[FieldOption] = (
    [FieldOption(**item) for item in google_metrics] +
    [FieldOption(**item) for item in google_dimensions] +
    [FieldOption(**item) for item in google_analytics_metrics] +
    [FieldOption(**item) for item in google_analytics_dimensions] +
    [FieldOption(**item) for item in facebook_metrics] +
    [FieldOption(**item) for item in facebook_dimensions] +
    [FieldOption(**item) for item in youtube_metrics] +
    [FieldOption(**item) for item in youtube_dimensions] + 
    [FieldOption(**item) for item in instagram_account_metrics] +
    [FieldOption(**item) for item in instagram_account_dimensions] +
    [FieldOption(**item) for item in instagram_media_metrics] +
    [FieldOption(**item) for item in instagram_media_dimensions] +
    [FieldOption(**item) for item in google_video_metrics] +
    [FieldOption(**item) for item in google_video_dimensions]
)


all_metrics: List[FieldOption] = (
    [FieldOption(**item) for item in google_metrics] +
    [FieldOption(**item) for item in google_analytics_metrics] +
    [FieldOption(**item) for item in facebook_metrics] +
    [FieldOption(**item) for item in youtube_metrics] + 
    [FieldOption(**item) for item in instagram_account_metrics] +
    [FieldOption(**item) for item in instagram_media_metrics]
)

all_dimensions: List[FieldOption] = (
    [FieldOption(**item) for item in google_dimensions] +
    [FieldOption(**item) for item in google_analytics_dimensions] +
    [FieldOption(**item) for item in facebook_dimensions] +
    [FieldOption(**item) for item in youtube_dimensions] + 
    [FieldOption(**item) for item in instagram_account_dimensions] +
    [FieldOption(**item) for item in instagram_media_dimensions]
)


def load_postgresql_table(table_name):
    try:
        # Read the table into a DataFrame using the engine
        df = pd.read_sql_table(table_name, con=engine)
        return df

    finally:
        # Close the engine
        engine.dispose()


def create_field_list(
    fields: List[FieldOption],
    use_alt_value: bool = False,
    split_value: bool = False,
    channel: ChannelType = None,
):
    """
    Creates a list of fields, metrics, and dimensions from a list of FieldOptions.

    Args:
        fields (List[FieldOption]): List of FieldOptions.
        use_alt_value (bool, optional): If True, uses the alt_value of the FieldOption. Defaults to False.
        split_value (bool, optional): If True, splits the value of the FieldOption by "." and uses the last element. Defaults to False.
        channel (ChannelType): type of channel (google or facebook)

    Returns:
        filtered_fields (List[str]): List of all fields.
        metrics (List[str]): List of all metrics.
        dimensions (List[str]): List of all dimensions.


    """
    if use_alt_value:
        metrics = [
            field.alt_value if field.alt_value is not None else field.value
            for field in fields
            if field.type == FieldType.metric
        ]
        dimensions = [
            field.alt_value if field.alt_value is not None else field.value
            for field in fields
            if field.type == FieldType.dimension
        ]
    else:
        metrics = [
            field.value
            for field in fields
            if field.type == FieldType.metric and field.value is not None
        ]
        dimensions = [
            field.value
            for field in fields
            if field.type == FieldType.dimension and field.value is not None
        ]

    filtered_fields = metrics + dimensions

    if split_value:
        filtered_fields = [f.split(".")[-1] for f in filtered_fields]

    filtered_fields = list(set(filtered_fields))

    return filtered_fields, metrics, dimensions


def fetch_data(data_source: DataSource):
    """
    Fetches data from a given data source.

    Args:
        data_source (DataSource): The data source to fetch data from.

    Returns:
        list: A list of fetched data.

    Raises:
        HTTPException: If the channel type is not supported.

    """
    print(data_source.adAccounts)
    data_list = []
    for adAccount in data_source.adAccounts:
        account_id = adAccount.id 
        fields, metrics, dimensions = create_field_list(
            data_source.fields, channel=adAccount.channel
        )

        # Builds query depending on the channel type
        if adAccount.channel == ChannelType.google:
            data_query = build_google_query(
                fields=fields,
                start_date=data_source.start_date,
                end_date=data_source.end_date,
            )
            query = GoogleQuery(
                account_id=adAccount.account_id, #  Use account id instead of id
                metrics=metrics,
                dimensions=dimensions,
                start_date=data_source.start_date,
                end_date=data_source.end_date,
                manager_id=adAccount.id
            )
            data = fetch_google_data(
                current_user=data_source.user, query=query, data_query=data_query
            )
        elif adAccount.channel == ChannelType.google_video:
            data_query = build_google_video_query(
                fields=fields,
                start_date=data_source.start_date,
                end_date=data_source.end_date,
            )
            query = GoogleQuery(
                account_id=adAccount.account_id, #  Use account id instead of id
                metrics=metrics,
                dimensions=dimensions,
                start_date=data_source.start_date,
                end_date=data_source.end_date,
                manager_id=adAccount.id
            )
            data = fetch_google_data(
                current_user=data_source.user, query=query, data_query=data_query
            )
        elif adAccount.channel == ChannelType.google_analytics:
            query = GoogleAnalyticsQuery(
                property_id=account_id,
                metrics=metrics,
                dimensions=dimensions,
                start_date=data_source.start_date,
                end_date=data_source.end_date,
            )
            data = fetch_google_analytics_data(
                current_user=data_source.user, query=query
            )
        elif adAccount.channel == ChannelType.facebook:
            query = FacebookQuery(
                account_id=account_id, metrics=metrics, dimensions=dimensions
            )
            data = fetch_facebook_data(current_user=data_source.user, query=query)
        elif adAccount.channel == ChannelType.instagram_media or adAccount.channel == ChannelType.instagram_account:
            query = InstagramQuery(
                account_id=account_id, metrics=metrics, dimensions=dimensions, channel=adAccount.channel
            )
            data = fetch_instagram_data(current_user=data_source.user, query=query)
        elif adAccount.channel == ChannelType.youtube:
            query = YoutubeQuery(
                account_id=account_id,
                metrics=metrics,
                dimensions=dimensions,
                start_date=data_source.start_date,
                end_date=data_source.end_date,
            )
            data = fetch_youtube_data(current_user=data_source.user, query=query)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Channel type { data_source.adAccount.channel} not supported.",
            )

        data_list.append(data)

    return data_list


def add_table_to_db(schema: str, table_name: str, df: pd.DataFrame):
    """
    Adds a table to the database.

    Parameters:
        schema (str): The name of the schema to add the table to.
        table_name (str): The name of the table to add.
        df (pd.DataFrame): The DataFrame containing the data to insert into the table.

    Returns:
        dict: A dictionary with a single key "message" and value "success" indicating that the table was successfully added to the database.
    """
    connection = engine.connect()
    if not engine.dialect.has_schema(connection, schema):
        # Create the schema
        engine.execute(f'CREATE SCHEMA "{schema}"')

    df.to_sql(
        table_name,
        engine,
        schema=schema,
        if_exists="replace",
        index=False,
        chunksize=100,
    )
    connection.close()

    return {"message": "success"}


def build_blend_query(
    fields: List[FieldOptionWithDataSourceId],
    join_conditions: List[JoinCondition],
    left_data_source: DataSourceInDB,
    right_data_source: DataSourceInDB,
    date_column: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """
    Builds a SQL query for blending data from two data sources.

    Args:
        fields (List[FieldOptionWithDataSourceId]): A list of field options with data source IDs.
        join_conditions (List[JoinCondition]): A list of join conditions.
        left_data_source (DataSourceInDB): The left data source.
        right_data_source (DataSourceInDB): The right data source.

    Returns:
        str: The SQL query for blending the data.
    """
    db_schema = left_data_source.db_schema
    left_table_name = left_data_source.name
    right_table_name = right_data_source.name

    field_names = []
    for field in fields:
        if field.data_source_id == left_data_source.id:
            field_name = f'"{left_table_name}"."{field.alt_value}"'
        elif field.data_source_id == right_data_source.id:
            field_name = f'"{right_table_name}"."{field.alt_value}"'
        else:
            raise ValueError("Invalid data source ID")
        field_names.append(field_name)

    query = f'SELECT DISTINCT {", ".join(field_names)} FROM {db_schema}."{left_table_name}" '
    for join_condition in join_conditions:
        query += f'{join_condition.join_type.value} {db_schema}."{right_table_name}" ON {db_schema}."{left_table_name}"."{join_condition.left_field.alt_value}" = {db_schema}."{right_table_name}"."{join_condition.right_field.alt_value}"'
    if date_column is not None and start_date is not None and end_date is not None:
        query += f"WHERE {date_column} BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'"

    return query


def airpipe_field_option(field_name: str, value = None):
    """
    Returns a FieldOption object for the given field name.

    Args:
        field_name (str): The name of the field for which the FieldOption object is created.

    Returns:
        FieldOption: An object representing a field option with various attributes such as value, label, type, channel, alt_value, and img.

    """
    # if value is type of a number, then type if FieldType.metric, otherwise it's FieldType.dimension
    if value:
        if isinstance(value, int) or isinstance(value, float):
            field_type = FieldType.metric
        else:
            field_type = FieldType.dimension
    else:
        field_type = FieldType.metric


    return FieldOption(value=field_name,
                       label=field_name.replace("_", " ").title(),
                       type=field_type,
                       channel=ChannelType.airpipe,
                       alt_value=field_name,
                       img="airpipe-field-icon")


def add_data_source_row_to_db(user: UserDB, ad_account: AdAccount, airbyte_source_id: Optional[str]) -> DataSourceDB: 
    """
    Inserts a new data source row into the database for the given user and ad account.
    
    Args:
        user (UserWithId): The user with id.
        ad_account (AdAccount): The ad account.
        airbyte_source_id (Optional[str]): The airbyte source id.
        
    Returns:
        DataSourceInDB: The data source row added to the database.
    """
    
    db_schema = f"_{user.id}"
    name = uuid.uuid4()
    table_name = f"{db_schema}.{name}"

    start_date = datetime.now()
    end_date = start_date - timedelta(days=365.25*2)

    data_source_row = DataSourceDB(
        user_id=user.id,
        db_schema=db_schema,
        name=name,
        table_name=table_name,
        fields='',
        channel=ad_account.channel,
        channel_img=ad_account.img,
        ad_account_id=ad_account.id,
        ad_account_name=ad_account.name,
        start_date=start_date, 
        end_date=end_date,
    )

    if airbyte_source_id:
        data_source_row.airbyte_source_id = airbyte_source_id

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

    return data_source_row

