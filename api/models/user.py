from pydantic import BaseModel
from typing import Optional, Union

from api.core.static_data import OnboardingStage, UserRoleType


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    email: str
    onboarding_stage: OnboardingStage = OnboardingStage.signed_up
    role: Optional[UserRoleType]
    facebook_access_token: Optional[str] = None
    google_refresh_token: Optional[str] = None
    google_analytics_refresh_token: Optional[str] = None
    google_sheets_refresh_token: Optional[str] = None
    youtube_refresh_token: Optional[str] = None
    instagram_access_token: Optional[str] = None
    airbyte_destination_id: Optional[str] = None


class UserWithId(User):
    id: int


class UserInDB(User):
    hashed_password: str
