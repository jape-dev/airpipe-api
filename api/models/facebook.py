from pydantic import BaseModel
from typing import List


class AdAccount(BaseModel):
    id: str
    account_id: str
    name: str


class FacebookQueryResults(BaseModel):
    results: List

    class Config:
        orm_mode = True


class FacebookQuery(BaseModel):
    account_id: str
    metrics: List[str]
    dimensions: List[str]
    start_date: int
    end_date: int
