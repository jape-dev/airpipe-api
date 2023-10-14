from fastapi import APIRouter, HTTPException

from api.core.google import get_access_token
from api.core.sheets import create_sheet, write_values
from api.models.sheets import SpreadsheetWithRefreshToken, SpreadsheetResponse

router = APIRouter(prefix="/sheets")


@router.post("/create", response_model=SpreadsheetResponse)
def create(spreadsheet: SpreadsheetWithRefreshToken) -> SpreadsheetResponse:
    access_token = get_access_token(spreadsheet.refresh_token)
    sheet = create_sheet(access_token, spreadsheet.title)

    if sheet.status_code == 200:
        id = sheet.json()["spreadsheetId"]
        url = sheet.json()["spreadsheetUrl"]
        values = write_values(
            access_token,
            sheet.json()["spreadsheetId"],
            spreadsheet.db_schema,
            spreadsheet.db_name,
        )

        if values.status_code == 200:
            return SpreadsheetResponse(id=id, url=url)
        else:
            raise HTTPException(status_code=400, detail=values.json())
    else:
        raise HTTPException(status_code=400, detail=sheet.json())
