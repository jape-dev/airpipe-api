from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional

from api.models.connector import AdAccount
from api.models.user import User
from api.core.static_data import ChannelType, FieldType, JoinType, ReportType, CustomField
from api.core.custom_fields import thumb_stop_ratio


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
    columns: List[str]
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
    channel: ChannelType
    alt_value: Optional[str] = None
    img: Optional[str]
    default: Optional[bool] = None
    custom_field: Optional[CustomField] = None


    def create_custom_field(self, table_id):
        
        if self.custom_field==CustomField.thumb_stop_ratio:
            return thumb_stop_ratio(table_id)


class FieldOptionWithDataSourceId(FieldOption):
    data_source_id: int


class DataSource(BaseModel):
    name: str
    user: User
    fields: List[FieldOption]
    adAccounts: List[AdAccount]
    start_date: datetime
    end_date: datetime


class DataSourceInDB(BaseModel):
    id: int
    user_id: str
    db_schema: str
    name: str
    table_name: str
    fields: str
    channel: str
    channel_img: str
    ad_account_id: str
    ad_account_name: Optional[str]
    start_date: datetime
    end_date: datetime
    dh_connection_id: Optional[str]


class DataPrompt(BaseModel):
    prompt: str
    table: str


class JoinCondition(BaseModel):
    left_field: FieldOption
    right_field: FieldOption
    join_type: JoinType
    left_data_source_id: int
    right_data_source_id: int


class View(BaseModel):
    name: str
    fields: List[FieldOption]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    join_conditions: Optional[List[JoinCondition]]


class ViewInDB(BaseModel):
    id: int
    user_id: str
    db_schema: str
    name: str
    table_name: str
    fields: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    dh_connection_id: Optional[str]

    class Config:
        orm_mode = True


class Table(BaseModel):
    id: int
    user_id: str
    db_schema: str
    name: str
    table_name: str
    label: str
    fields: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    channel: Optional[ChannelType]
    channel_img: Optional[str]
    ad_account_id: Optional[str]
    ad_account_name: Optional[str]
    dh_connection_id: Optional[str]


class ChartData(BaseModel):
    chart_id: str
    data: CurrentResults
    chart_type: str
    selected_dimension: FieldOption
    selected_metric: FieldOption
    primary_color: str
    secondary_color: str
    slice_colors: List[str]
    field_options: List[FieldOption]
    title:str
    caption:str
