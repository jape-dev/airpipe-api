from fastapi import APIRouter
import openai
from typing import List

from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.chains import SQLDatabaseChain

from api.config import Config
from api.models.codex import Prompt, ChainResult
from api.models.data import DataSourceInDB
from api.utilities.string import remove_decimal
from api.utilities.data import tuples_to_recharts_dict
from api.utilities.prompt import (
    get_missing_column_prompt,
    get_ambiguity_prompt,
    extract_columns,
)
from api.utilities.gpt import chat_completion
from api.core.codex import debug_agent, get_din_sql


OPEN_API_KEY = Config.OPEN_API_KEY
DATABASE_URL = Config.DATABASE_URL


router = APIRouter()


@router.post("/ask_question", response_model=ChainResult, status_code=200)
def ask_question(prompt: Prompt) -> ChainResult:
    llm_openapi = OpenAI(
        temperature=0,
        openai_api_key=OPEN_API_KEY,
    )

    table_name = prompt.table
    db = SQLDatabase.from_uri(DATABASE_URL, include_tables=[table_name])

    missing_prompt = get_missing_column_prompt(db.table_info, db.dialect, prompt.input)

    print(missing_prompt)
    missing_completion = chat_completion(missing_prompt)
    missing_columns = extract_columns(missing_completion)
    print(missing_columns)

    ambiguity_prompt = get_ambiguity_prompt(db.table_info, db.dialect, prompt.input)
    ambiguity_completion = chat_completion(ambiguity_prompt)
    ambiguity_columns = extract_columns(ambiguity_completion)

    db_chain = SQLDatabaseChain(
        llm=llm_openapi,
        database=db,
        verbose=True,
        return_intermediate_steps=True,
        top_k=100,
    )

    input = prompt.input
    result = db_chain(input)

    print(result)
    query = result["intermediate_steps"][0]

    if len(missing_columns) > 0:
        answer = "Please provide the following columns: " + ", ".join(missing_columns)
        result = ChainResult(answer=answer, column_options=missing_columns)
    elif len(ambiguity_columns) > 0:
        answer = "Please clarify the following columns: " + ", ".join(ambiguity_columns)
        result = ChainResult(answer=answer, column_options=ambiguity_columns)
    else:
        db_chain = SQLDatabaseChain(
            llm=llm_openapi,
            database=db,
            verbose=True,
            return_intermediate_steps=True,
            top_k=100,
        )

        input = prompt.input
        result = db_chain(input)

        data = remove_decimal(result["intermediate_steps"][-1])
        data_json = tuples_to_recharts_dict(data)
        answer = result["result"]

        result = ChainResult(result=data_json, answer=answer)

    return result


@router.post("/chart_type", status_code=200)
def chart_type(input: str) -> str:
    prompt = f"The following are the possible chart types supported by the code provided: area, bar, line, composed, scatter, pie, radar, radialBar, treemap, and funnel. Given the data: {input}, identify the chart type the user wants to display. Return just one word"

    openai.api_key = OPEN_API_KEY

    message = [{"role": "user", "content": prompt}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message,
        temperature=0,
        max_tokens=10,
        n=1,
        frequency_penalty=0.5,
        presence_penalty=0.5,
    )

    completion = response.choices[0].message["content"]

    return completion


@router.post("/din_sql", status_code=200)
def din_sql(question: str, data_sources: List[DataSourceInDB]) -> str:
    sql = get_din_sql(question, data_sources)
    sql = debug_agent(question, sql, data_sources)

    return sql
