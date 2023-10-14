from pydantic import BaseModel
from typing import Optional, Union

from api.core.static_data import OnboardingStage


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    email: str
    onboarding_stage: OnboardingStage = OnboardingStage.connect
    facebook_access_token: Optional[str] = None
    google_refresh_token: Optional[str] = None
    google_analytics_refresh_token: Optional[str] = None
    google_sheets_refresh_token: Optional[str] = None


class UserWithId(User):
    id: int


class UserInDB(User):
    hashed_password: str
