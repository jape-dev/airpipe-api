from api.models.data import DataSource
from typing import Optional
import random, string
import json


def get_keys(list_of_dicts):
    if list_of_dicts:
        first_dict = list_of_dicts[0]
        keys_list = list(first_dict.keys())
        return keys_list
    else:
        return []


def create_table_name(data_source: DataSource, id: Optional[int] = None) -> str:
    if id is None:
        id = "".join(
            random.SystemRandom().choice(string.ascii_lowercase + string.digits)
            for _ in range(4)
        )

    data_source_name = data_source.name.replace(" ", "_")
    data_source_name = data_source_name.replace("-", "_")

    table_name = data_source.adAccount.channel + data_source_name + id
    return table_name


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

    name_list = ["averageCpc", "averageCpe", "averageCpm", "costPerConversion", "averageCpv", "costMicros"]


    if str(name) in name_list:
        metric = metric / 1000000.0
        metric = round(metric, 2)
    return metric

