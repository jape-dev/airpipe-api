from pydantic import BaseModel, Field
from typing import List, Optional


class Completion(BaseModel):
    completion: str = Field(...)


class Prompt(BaseModel):
    input: str
    tables: List[str]


class ChainResult(BaseModel):
    result: Optional[List]
    answer: str
    column_options: Optional[List[str]]


class AmbiguousColumns(BaseModel):
    statement: str
    term: List
    columns: List
