from api.models.data import DataSource


def get_keys(list_of_dicts):
    if list_of_dicts:
        first_dict = list_of_dicts[0]
        keys_list = list(first_dict.keys())
        return keys_list
    else:
        return []


def create_table_name(data_source: DataSource, data_source_id: int) -> str:
    table_name = f"{data_source.adAccount.channel}-{data_source.name}-{data_source_id}"
    return table_name
