from api.models.data import DataSource
from typing import Optional
import random, string


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
