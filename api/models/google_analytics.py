from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class GoogleAnalyticsQueryResults(BaseModel):
    results: List

    class Config:
        orm_mode = True


class GoogleAnalyticsQuery(BaseModel):
    property_id: str
    metrics: List[str]
    dimensions: List[str]
    start_date: datetime
    end_date: datetime
