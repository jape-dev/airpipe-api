from pydantic import BaseModel
from typing import List


class AdAccount(BaseModel):
    id: str
    account_id: str
    name: str


class FacebookQueryResults(BaseModel):
    id: str


class FacebookQuery(BaseModel):
    metrics: List[str]
    dimensions: List[str]
    start_date: int
    end_date: int