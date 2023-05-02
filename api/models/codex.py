from pydantic import BaseModel, Field


class Completion(BaseModel):
    completion: str = Field(...)


class Prompt(BaseModel):
    prompt:str
    table: str