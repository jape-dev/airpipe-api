from pydantic import BaseModel
from typing import List, Optional
from api.core.static_data import ChannelType


class AdAccount(BaseModel):
    id: str
    account_id: str
    name: str


class InstagramQuery(BaseModel):
    account_id: str
    metrics: List[str]
    dimensions: List[str]
    period: str = "day"
    start_date: Optional[int]
    end_date: Optional[int]
    channel: ChannelType = ChannelType.instagram_media
