from pydantic import BaseModel

from api.core.static_data import LookerFieldType, FieldType


class LookerField(BaseModel):
    id: str
    name: str
    looker_field_type: LookerFieldType
    field_type: FieldType
