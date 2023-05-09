from pydantic import BaseModel, Field
from typing import List


class Completion(BaseModel):
    completion: str = Field(...)


class Prompt(BaseModel):
    prompt: str
    table: str


class ChainResult(BaseModel):
    sql_result: List
    string_result: str
    json_result: List
    answer: str
