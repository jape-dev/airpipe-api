from typing import List
from api.models.data import FieldOption
from api.core.static_data import FieldType


def create_field_list(
    fields: List[FieldOption], use_alt_value=False, split_value=False
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

    all_fields = metrics + dimensions
    all_fields, metrics, dimensions

    if split_value:
        all_fields = [f.split(".")[-1] for f in all_fields]

    return all_fields, metrics, dimensions
