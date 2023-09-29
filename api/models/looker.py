from pydantic import BaseModel
from typing import List, Optional

from api.core.static_data import LookerFieldType


class LookerField(BaseModel):
    name: str
    type: LookerFieldType
