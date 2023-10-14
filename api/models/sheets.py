from pydantic import BaseModel
from typing import Optional


class Spreadsheet(BaseModel):
    title: str
    sheet_name: Optional[str]
    db_schema: str
    db_name: str


class SpreadsheetWithRefreshToken(Spreadsheet):
    refresh_token: str


class SpreadsheetResponse(BaseModel):
    id: str
    url: str
