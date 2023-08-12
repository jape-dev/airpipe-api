from pydantic import BaseModel
from typing import List, Optional

from api.models.user import User


class Message(BaseModel):
    is_user_message: bool
    current_user: Optional[User]
    text: Optional[str]
    data: Optional[List[object]]
    columns: Optional[List[str]]
    loading: Optional[bool]
    table_name: Optional[str]


class Conversation(BaseModel):
    messages: List[Message]
