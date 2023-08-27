from pydantic import BaseModel
from api.core.static_data import Environment


class Contact(BaseModel):
    email: str
    environment: Environment = Environment.production
