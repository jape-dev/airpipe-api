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


class BaseAmbiguities(BaseModel):
    question: str
    statement: str
    term: List


class AmbiguousColumns(BaseAmbiguities):
    columns: List


class CaptionData(BaseModel):
    data: List
    chart_type: str