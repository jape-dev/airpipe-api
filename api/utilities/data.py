from collections import defaultdict
import pandas as pd
from typing import List
import json
from sqlalchemy import MetaData
from sqlalchemy.inspection import inspect

from api.database.database import engine
from api.models.data import FieldOption
from api.core.static_data import (
    ChannelType,
    google_metrics,
    google_dimensions,
    google_analytics_metrics,
    google_analytics_dimensions,
    facebook_metrics,
    facebook_dimensions,
)


def get_keys(list_of_dicts):
    if list_of_dicts:
        first_dict = list_of_dicts[0]
        keys_list = list(first_dict.keys())
        return keys_list
    else:
        return []


def tuples_to_dicts(tuples_list, as_json=False):
    # Initialize an empty list to hold the dictionaries
    dicts_list = []

    # Loop through each tuple in the input list
    for tup in tuples_list:
        # If the tuple has only one value, add a default key name 'field'
        if len(tup) == 1:
            new_dict = {"field": tup[0]}
        else:
            # Create a dictionary with keys and values from the tuple
            new_dict = {tup[i]: tup[i + 1] for i in range(0, len(tup), 2)}
        # Add the new dictionary to the list
        dicts_list.append(new_dict)

    # If as_json is True, convert the list of dictionaries to a list of JSON strings
    if as_json:
        json_list = [json.dumps(d) for d in dicts_list]
        return json_list

    # Otherwise, return the list of dictionaries
    return dicts_list


def tuples_to_recharts_dict(tuples_list, as_json=False):
    # Initialize an empty list to hold the JSON strings
    dicts_list = []

    # Loop through each tuple in the input list
    for tup in tuples_list:
        # If the tuple has only one value, add a default key name 'field'
        if len(tup) == 1:
            new_dict = {"name": "field", "value": tup[0], "color": "#14B8A6"}
        else:
            # Create a dictionary with keys and values from the tuple
            new_dict = {"name": tup[0], "value": tup[1], "color": "#14B8A6"}
        # Convert the dictionary to a JSON string and add it to the list
        dicts_list.append(new_dict)

    # If as_json is True, convert the list of dictionaries to a list of JSON strings
    if as_json:
        json_list = [json.dumps(d) for d in dicts_list]
        return json_list

    # Return the list of JSON strings
    return dicts_list


def convert_metric(metric, name: str):
    name_list = [
        "averageCpc",
        "averageCpe",
        "averageCpm",
        "costPerConversion",
        "averageCpv",
        "costMicros",
    ]

    if str(name) in name_list:
        metric = float(metric) / 1000000.0
        metric = round(metric, 2)
    return metric


def get_table_schema(schema: str, table_name: str):
    """
    Get the table schema

    Args:
        table_name (str): The name of the table

    Returns:
        list: A list of column names

    """
    # Create a metadata object
    metadata = MetaData(bind=engine, schema=schema)
    metadata.reflect()

    # Get the table object using the inspector
    table = metadata.tables.get(table_name)

    # Check if the table exists
    if table is not None:
        # Use SQLAlchemy's inspector to get the column names
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name, schema=schema)

        # Extract the column names
        column_names = [column["name"] for column in columns]
        return column_names
    else:
        print("table could not be found")
        return None


def merge_objects(object_lists):
    """
    Merge multiple lists of objects into a single list based on their date.

    Parameters:
    - object_lists (list of lists of dictionaries): A list of lists containing objects in the form of dictionaries. Each dictionary represents an object with a "date" key and additional key-value pairs.

    Returns:
    - merged_list (list of dictionaries): A list of dictionaries representing the merged objects. Each dictionary contains a "date" key and the merged key-value pairs from the input objects.

    Algorithm:
    1. Create an empty dictionary called date_dict to store objects based on their date.
    2. Iterate over each list in object_lists.
    3. For each object in the current list, get its date and retrieve the existing object from date_dict based on the date.
    4. Merge the key-value pairs of the current object into the existing object, excluding the "date" key.
    5. Update the object in date_dict with the merged key-value pairs.
    6. Convert date_dict back to a list of dictionaries called merged_list.
    7. Return the merged_list.

    Example Usage:
    object_lists = [
        [{"date": "2022-01-01", "name": "John"}, {"date": "2022-01-01", "age": 30}],
        [{"date": "2022-01-02", "name": "Jane"}, {"date": "2022-01-02", "city": "New York"}]
    ]
    merged_list = merge_objects(object_lists)
    print(merged_list)
    # Output: [{"date": "2022-01-01", "name": "John", "age": 30}, {"date": "2022-01-02", "name": "Jane", "city": "New York"}]

    """

    # Create a dictionary to store objects based on their date
    date_dict = {}

    # Merge objects from all input lists into date_dict
    for obj_list in object_lists:
        for obj in obj_list:
            date = obj["date"]
            # Use a defaultdict as I'm going to add
            existing_obj = date_dict.get(date, defaultdict(list))
            for key, value in obj.items():
                if key != "date":
                    if key not in existing_obj:
                        existing_obj[key] = []
                    existing_obj[key].append(value)
            date_dict[date] = existing_obj

    return date_dict


def pad_object_list(data: dict):
    """
    Pad the lists in a dictionary of dictionaries with None values to make them the same length.

    Parameters:
        data (dict): A dictionary of dictionaries where the values are lists.

    Returns:
        dict: The modified dictionary with padded lists.
    """
    print(data)

    # Find the maximum length of lists in the nested dictionaries
    max_length = max(
        max(len(lst) for lst in inner_dict.values()) for inner_dict in data.values()
    )

    # Pad the lists with None values to make them the same length
    for inner_dict in data.values():
        max_length = max(len(lst) for lst in inner_dict.values())
        for key in inner_dict:
            inner_dict[key] += [None] * (max_length - len(inner_dict[key]))

    return data


def object_list_to_df(data: dict):
    """
    Generate a DataFrame from a dictionary of object lists.

    Parameters:
        data (dict): A dictionary containing object lists as values.

    Returns:
        df (pandas.DataFrame): The generated DataFrame.
    """
    # Create an empty DataFrame
    df_data = []

    # Loop through the date and values dictionary
    for date, values in data.items():
        # Find the maximum number of values in any key for the current date
        max_values = max(len(val_list) for val_list in values.values())

        # Iterate over the range of maximum values
        for i in range(max_values):
            row = {"date": date}  # Initialize a row with the current date

            # Iterate through each key and its corresponding value list
            for key, val_list in values.items():
                if i < len(val_list):
                    row[key] = val_list[i]  # If there's a value at index 'i', use it
                else:
                    row[key] = date  # If not, use the current date as padding

            df_data.append(row)  # Append the row to the DataFrame data list

    # Create a DataFrame from the data list
    df = pd.DataFrame(df_data)

    # Convert the DataFrame numerica values to numeric
    df = df.apply(pd.to_numeric, errors="ignore")

    return df


def insert_alt_values(data: List[object], fields: List[FieldOption]):
    """
    Replaces specific keys in a list of dictionaries with their corresponding values from a given list of FieldOptions.

    Args:
        data (List[object]): A list of dictionaries representing the data to be modified.
        fields (List[FieldOption]): A list of FieldOptions containing the mapping of keys to their corresponding alt_values.

    Returns:
        List[object]: The modified list of dictionaries with the specified keys replaced by their corresponding alt_values.
    """
    field_lookup = {field.value: field.alt_value for field in fields}

    for item in data:
        for key in list(item.keys()):
            if key in field_lookup:
                item[field_lookup[key]] = item.pop(key)

    return data


def get_channel_img(fields: List[FieldOption]):
    # Get the unique field.img from fields
    field_img = [field.img for field in fields]
    # Get unique values from field_img
    unique_field_img = list(set(field_img))

    if len(unique_field_img) > 1:
        return "table-icon"
    else:
        return unique_field_img[0]


def all_channel_fields() -> List[FieldOption]:
    """
    Merge channel options.

    Returns:
        all_channels (list): A list containing all channel options merged together.
    """
    all_channels = (
        google_metrics
        + google_dimensions
        + google_analytics_metrics
        + google_analytics_dimensions
        + facebook_metrics
        + facebook_dimensions
    )

    return all_channels


def get_channel_name_from_enum(channel: str):
    if channel == ChannelType.google.value:
        return "Google Ads"
    elif channel == ChannelType.facebook.value:
        return "Facebook Ads"
    elif channel == ChannelType.google_analytics.value:
        return "Google Analytics"
