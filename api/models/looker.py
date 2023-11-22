from pydantic import BaseModel
from typing import List

from api.core.static_data import LookerFieldType, FieldType


class LookerField(BaseModel):
    id: str
    name: str
    looker_field_type: LookerFieldType
    field_type: FieldType


class LookerDataRequest(BaseModel):
    db_schema: str
    name: str
    fields: List[str]


class LookerTable(BaseModel):
    db_schema: str
    name: str
    label: str
