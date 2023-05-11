from pydantic import BaseModel
from typing import List, Optional


class GoogleQueryResults(BaseModel):
    results: List

    class Config:
        orm_mode = True


class GoogleQuery(BaseModel):
    account_id: str
    metrics: List[str]
    dimensions: List[str]
    start_date: Optional[int]
    end_date: Optional[int]
