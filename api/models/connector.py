from pydantic import BaseModel
from typing import List, Optional


class AdAccount(BaseModel):
    id: str
    account_id: Optional[str]
    name: Optional[str]
