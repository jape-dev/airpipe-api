from pydantic import BaseModel
from typing import List
from datetime import datetime


class YoutubeQuery(BaseModel):
    account_id: str
    metrics: List[str]
    dimensions: List[str]
    start_date: datetime
    end_date: datetime
