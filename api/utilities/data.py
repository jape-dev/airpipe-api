from api.models.data import DataSource
from typing import Optional, List
import random, string
import json
from sqlalchemy import MetaData
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker

from api.database.database import session, engine
from api.models.data import FieldOption


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
    merged_list = []

    # Create a dictionary to store objects based on their date
    date_dict = {}

    # Merge objects from all input lists into date_dict
    for obj_list in object_lists:
        for obj in obj_list:
            date = obj["date"]
            existing_obj = date_dict.get(date, {})
            for key, value in obj.items():
                if key != "date":
                    existing_obj[key] = value
            date_dict[date] = existing_obj

    # Convert date_dict back to a list of objects
    for date, obj in date_dict.items():
        merged_list.append({"date": date, **obj})

    return merged_list


def insert_alt_values(data: List[object], fields: List[FieldOption]):
    field_lookup = {field.value: field.alt_value for field in fields}

    for item in data:
        for key in list(item.keys()):
            if key in field_lookup:
                item[field_lookup[key]] = item.pop(key)

    return data
