from fastapi import HTTPException
import json
import requests
import sqlalchemy

from api.database.database import engine, session


def create_sheet(access_token: str, title: str):
    """
    Create a new Google Sheets spreadsheet with the given title.

    Args:
        access_token (str): The access token for authorizing the request.
        title (str): The title of the new spreadsheet.

    Returns:
        response: The response object containing the result of the API call.
    """

    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://sheets.googleapis.com/v4/spreadsheets"
    body = json.dumps(
        {
            "properties": {
                "title": title,
            }
        }
    )

    response = requests.post(url, headers=headers, data=body)

    return response


def write_values(token: str, spreadsheet_id: str, schema: str, name: str):
    connection = engine.connect()

    try:
        query = f'SELECT * FROM {schema}."{name}"'
        results = connection.execute(query)
    except sqlalchemy.exc.ProgrammingError as e:
        print(e)
        connection.close()
        raise HTTPException(status_code=400, detail=f"Error executing query: {e}")

    keys = results.keys()
    data = results.all()

    # Calculate the range based on the size of the result
    range_start = "A1"
    range_end = chr(ord(range_start[0]) + len(keys) - 1) + str(len(data) + 1)
    range = f"{range_start}:{range_end}"

    # Append the keys and values together.
    values = [list(keys)] + [list(result) for result in data]

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values:batchUpdate"
    body = json.dumps(
        {
            "valueInputOption": "USER_ENTERED",
            "data": [
                {
                    "range": range,
                    "majorDimension": "ROWS",
                    "values": values,
                },
            ],
        }
    )

    response = requests.post(
        url, headers={"Authorization": f"Bearer {token}"}, data=body
    )

    connection.close()

    return response
