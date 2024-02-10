from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class GoogleQuery(BaseModel):
    account_id: str
    metrics: List[str]
    dimensions: List[str]
    start_date: datetime
    end_date: datetime
    manager_id: Optional[str]
