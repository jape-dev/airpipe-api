from api.core.static_data import LookerFieldType, FieldType
from api.utilities.data import all_channel_fields
from api.models.looker import LookerField

postgres_to_looker_mapping = {
    "bigint": LookerFieldType.number,
    "int8": LookerFieldType.number,
    "bigserial": LookerFieldType.number,
    "bit": LookerFieldType.text,
    "bit varying": LookerFieldType.text,
    "varbit": LookerFieldType.text,
    "boolean": LookerFieldType.boolean,
    "bool": LookerFieldType.boolean,
    "bytea": LookerFieldType.text,
    "character": LookerFieldType.text,
    "char": LookerFieldType.text,
    "character varying": LookerFieldType.text,
    "varchar": LookerFieldType.text,
    "cidr": LookerFieldType.text,
    "circle": LookerFieldType.text,
    "date": LookerFieldType.date,
    "double precision": LookerFieldType.number,
    "float8": LookerFieldType.number,
    "inet": LookerFieldType.text,
    "integer": LookerFieldType.number,
    "int": LookerFieldType.number,
    "int4": LookerFieldType.number,
    "interval": LookerFieldType.text,
    "json": LookerFieldType.text,
    "jsonb": LookerFieldType.text,
    "line": LookerFieldType.text,
    "lseg": LookerFieldType.text,
    "macaddr": LookerFieldType.text,
    "macaddr8": LookerFieldType.text,
    "money": LookerFieldType.number,
    "numeric": LookerFieldType.number,
    "decimal": LookerFieldType.number,
    "path": LookerFieldType.text,
    "pg_lsn": LookerFieldType.text,
    "pg_snapshot": LookerFieldType.text,
    "point": LookerFieldType.text,
    "polygon": LookerFieldType.text,
    "real": LookerFieldType.number,
    "float4": LookerFieldType.number,
    "smallint": LookerFieldType.number,
    "int2": LookerFieldType.number,
    "smallserial": LookerFieldType.number,
    "serial2": LookerFieldType.number,
    "serial": LookerFieldType.number,
    "serial4": LookerFieldType.number,
    "text": LookerFieldType.text,
    "time": LookerFieldType.text,
    "timetz": LookerFieldType.text,
    "timestamp": LookerFieldType.text,
    "timestamptz": LookerFieldType.text,
    "tsquery": LookerFieldType.text,
    "tsvector": LookerFieldType.text,
    "txid_snapshot": LookerFieldType.text,
    "uuid": LookerFieldType.text,
    "xml": LookerFieldType.text,
}


def map_postgres_type_to_looker_type(schema: dict):
    """
    Generates a mapping of Postgres types to Looker types based on the provided schema.

    Args:
        schema (dict): A dictionary representing the schema, where the keys are field names and the values are Postgres types.

    Returns:s
        dict: A dictionary representing the mapping of field names to Looker types.

    """
    mapping = {}
    for field, type in schema.items():
        if type in postgres_to_looker_mapping:
            mapping[field] = postgres_to_looker_mapping[type]

    return mapping


def get_looker_fields(schema: dict):
    """
    Generates the list of Looker fields based on the given schema.

    Args:
        schema (dict): A dictionary representing the schema.

    Returns:
        list: A list of LookerField objects.
    """
    channel_fields = all_channel_fields()

    looker_fields = []
    for field, type in schema.items():
        if field == "date":
            looker_field = LookerField(
                id="datee",
                name="Date",
                looker_field_type=LookerFieldType.date,
                field_type=FieldType.dimension,
            )
            looker_fields.append(looker_field)

        else:
            matching_field = [
                channel_field
                for channel_field in channel_fields
                if channel_field["alt_value"] == field
            ][0]
            looker_field = LookerField(
                id=field,
                name=matching_field["label"],
                looker_field_type=type,
                field_type=matching_field["type"],
            )
            looker_fields.append(looker_field)

    return looker_fields
