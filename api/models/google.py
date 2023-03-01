from pydantic import BaseModel
from typing import List


class AdAccount(BaseModel):
    id: str


class GoogleQueryResults(BaseModel):
    results: List

    class Config:
        orm_mode = True


class GoogleQuery(BaseModel):
    account_id: str
    metrics: List[str]
    dimensions: List[str]
    start_date: int
    end_date: int
