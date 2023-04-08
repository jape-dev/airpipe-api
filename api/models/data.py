from pydantic import BaseModel
from typing import List, Dict, Optional


class TableColumns(BaseModel):
    name: str
    columns: List[str]

    class Config:
        orm_mode = True


class TabData(BaseModel):
    tabIndex: int
    data: List[TableColumns]


class Schema(BaseModel):
    tabs: List[TabData]


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


class DebugResponse(BaseModel):
    prompt: Optional[str]
    query: str
    error: str
    completion: str
