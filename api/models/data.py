from pydantic import BaseModel
from typing import List, Dict


class TableColumns(BaseModel):
    name: str
    columns: List[str]

    class Config:
        orm_mode = True


class SqlQuery(BaseModel):
    query: str

    class Config:
        orm_mode = True


class CurrentResults(BaseModel):
    name: str
    columns: List[str]
    results: List[Dict]


class QueryResults(BaseModel):
    results: List

    class Config:
        orm_mode = True
