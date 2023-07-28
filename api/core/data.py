from fastapi import HTTPException
import pandas as pd
from typing import List

from api.core.google import build_google_query, fetch_google_query
from api.core.facebook import fetch_facebook_data
from api.database.database import engine
from api.models.data import FieldOption, DataSource
from api.models.google import GoogleQuery
from api.models.facebook import FacebookQuery
from api.core.static_data import FieldType, ChannelType
from api.core.google_analytics import fetch_google_analytics_data
from api.models.google_analytics import GoogleAnalyticsQuery


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

    Returns:
        all_fields (List[str]): List of all fields.
        metrics (List[str]): List of all metrics.
        dimensions (List[str]): List of all dimensions.
        channel (ChannelType): type of channel (google or facebook)

    """
    if channel:
        fields = [field for field in fields if field.channel == channel]
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

    all_fields = metrics + dimensions

    if split_value:
        all_fields = [f.split(".")[-1] for f in all_fields]

    all_fields = list(set(all_fields))

    return all_fields, metrics, dimensions


def fetch_data(data_source: DataSource):
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
                account_id=account_id,
                metrics=metrics,
                dimensions=dimensions,
                start_date=data_source.start_date,
                end_date=data_source.end_date,
            )
            data = fetch_google_query(
                current_user=data_source.user, query=query, data_query=data_query
            )
        elif adAccount.channel == ChannelType.google_analytics:
            print("dataSource", data_source)
            print("dataSource metrics", metrics)

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
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Channel type { data_source.adAccount.channel} not supported.",
            )

        data_list.append(data)

    return data_list
