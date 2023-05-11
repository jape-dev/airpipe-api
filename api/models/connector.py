from pydantic import BaseModel
from typing import List, Optional
from api.core.static_data import ChannelType


class AdAccount(BaseModel):
    id: str
    channel: ChannelType
    account_id: Optional[str]
    name: Optional[str]
    img: Optional[str]
