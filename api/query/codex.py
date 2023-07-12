from fastapi import APIRouter
import openai
from typing import List
import re

from langchain import PromptTemplate, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.chains import SQLDatabaseChain

from api.config import Config
from api.models.codex import Prompt, ChainResult, AmbiguousColumns
from api.models.data import DataSourceInDB
from api.utilities.gpt import get_message_history
from api.utilities.string import remove_decimal
from api.utilities.data import tuples_to_recharts_dict
from api.utilities.prompt import (
    get_missing_column_prompt,
    get_ambiguity_prompt,
    extract_columns,
    ambiguity_prompt_maker,
    schema_linking_prompt_maker,
)
from api.utilities.gpt import chat_completion, din_completion
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
    missing_completion = chat_completion(missing_prompt)
    missing_columns = extract_columns(missing_completion)

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


@router.post("/schema_links")
def schema_links(question: str, data_sources: List[DataSourceInDB]) -> str:
    prompt = schema_linking_prompt_maker(question, data_sources)
    schema_links = din_completion(prompt)
    # try:
    #     schema_links = schema_links.split("Schema_links: ")[1]
    # except BaseException:
    #     print("Slicing error for the schema_linking module")
    #     schema_links = "[]"

    return schema_links


@router.post("/handle_ambiguity", status_code=200)
def ambiguity_checker(
    input: str, data_sources: List[DataSourceInDB], session_id: str
) -> str:
    history = get_message_history(session_id)
    messages = history.messages

    if len(messages) == 0:
        history.add_user_message(input)
        prompt = schema_linking_prompt_maker(input, data_sources)
        schema_links = din_completion(prompt)
        tables_names = [ds.table_name for ds in data_sources]
        db = SQLDatabase.from_uri(DATABASE_URL, include_tables=tables_names)
        table_info = db.table_info
        prompt = ambiguity_prompt_maker(table_info, input, schema_links)
        guide = din_completion(prompt)

    else:
        # Okay so now memory works - need to find an exit point
        prompt = schema_linking_prompt_maker(messages[0].content, data_sources)
        schema_links = din_completion(prompt)
        tables_names = [ds.table_name for ds in data_sources]
        db = SQLDatabase.from_uri(DATABASE_URL, include_tables=tables_names)
        table_info = db.table_info

        prefix = f"""
        You are a helpful AI SQL analyst having a conversaion with a human that guides the user to refine their question based on available
        tables and columns:

        {table_info}

        and schema_links: {schema_links}

        """

        template = (
            prefix
            + """
        The conversation so far:
        {chat_history}
        Human: {human_input}

        Given the user's original question, ask the user to clairfy what they mean
        in order to select the right schema_link. This includes any ambiguous column names.

        Return the question in the format:

        Clarification: clarification question here

        If it is already clear what the schema_link needs to be used. Just return 
        Clarification: complete

        """
        )

        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"],
            template=template,
        )
        memory = ConversationBufferMemory(memory_key="chat_history", history=history)

        llm_chain = LLMChain(
            llm=OpenAI(temperature=0, openai_api_key=OPEN_API_KEY),
            verbose=True,
            prompt=prompt,
            memory=memory,
        )
        guide = llm_chain.predict(human_input=input)
        history.add_user_message(input)

    history.add_ai_message(guide)
    return guide


@router.post("/check_ambiguous_columns", status_code=200)
def check_ambiguous_columns(
    input: str, data_sources: List[DataSourceInDB]
) -> AmbiguousColumns:
    prompt = ambiguity_prompt_maker(input, data_sources)
    ambiguities = din_completion(prompt)

    try:
        ambiguities = ambiguities.split("Ambiguity: ")[1]
    except BaseException:
        print("Slicing error for the ambiguity module")
        ambiguities = "[]"

    if ambiguities == "":
        return None
    else:
        term = re.findall(r'"([^"]*)"', ambiguities)
        columns = re.findall(r"\[(.*?)\]", ambiguities)
        ambigious_columns = AmbiguousColumns(
            statement=ambiguities, term=term, columns=columns
        )

    return ambigious_columns
