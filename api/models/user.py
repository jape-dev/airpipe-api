from pydantic import BaseModel
from typing import Optional, Union


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    email: str
    hashed_password: str
    facebook_access_token: Optional[str] = None
    google_access_token: Optional[str] = None
    access_token: Optional[str] = None


class UserInDB(User):
    hashed_password: str
