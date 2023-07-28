from pydantic import BaseModel
from typing import List, Optional


class GoogleQuery(BaseModel):
    account_id: str
    metrics: List[str]
    dimensions: List[str]
    start_date: str
    end_date: str
