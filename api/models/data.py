from pydantic import BaseModel
from typing import List, Dict, Optional

from api.models.connector import AdAccount
from api.models.user import User
from api.core.static_data import FieldType


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


class FieldOption(BaseModel):
    value: str
    label: str
    type: FieldType
    alt_value: Optional[str] = None


class DataSource(BaseModel):
    name: str
    user: User
    fields: List[FieldOption]
    adAccount: AdAccount
    start_date: str
    end_date: str


class DataSourceInDB(BaseModel):
    id: int
    user_id: str
    name: str
    table_name: str
    fields: str
    channel: str
    channel_img: str
    ad_account_id: str
    start_date: str
    end_date: str


class DataPrompt(BaseModel):
    prompt: str
    table: str
