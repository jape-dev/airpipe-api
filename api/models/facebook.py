from pydantic import BaseModel
from typing import List, Optional


class AdAccount(BaseModel):
    id: str
    account_id: str
    name: str


class FacebookQuery(BaseModel):
    account_id: str
    metrics: List[str]
    dimensions: List[str]
    start_date: Optional[int]
    end_date: Optional[int]
