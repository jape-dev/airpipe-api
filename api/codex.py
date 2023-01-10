from pydantic import BaseModel, Field


class Completion(BaseModel):
    completion: str = Field(...)