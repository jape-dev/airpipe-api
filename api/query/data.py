from api.models.data import TableColumns, CurrentResults, QueryResults
from api.database.database import engine

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
import pandas as pd
import sqlalchemy


router = APIRouter()


@router.get("/table_columns", response_model=TableColumns, status_code=200)
def get_table_columns(table_name: str):
    connection = engine.connect()
    result = connection.execute(f"SELECT * FROM {table_name} LIMIT 1")
    cols = [col for col in result.keys()]
    table_columns = TableColumns(name=table_name, columns=cols)

    return table_columns


@router.get("/run_query", response_model=QueryResults, status_code=200)
def run_query(query: str):
    connection = engine.connect()
    try:
        results = connection.execute(query)
    except sqlalchemy.exc.ProgrammingError as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)

    query_results = QueryResults(results=results.all())

    return query_results


@router.post("/create_new_table")
def create_new_table(results: CurrentResults = Body(...)):
    df = pd.DataFrame(results.results, columns=results.columns)
    df = df.apply(pd.to_numeric, errors="ignore")
    df.to_sql(results.name, engine, if_exists="replace", index=False)

    return {"message": "success"}
