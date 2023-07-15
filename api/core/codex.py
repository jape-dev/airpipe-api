import datetime
import openai
import re
from typing import List, Union
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents.agent_types import AgentType
from langchain import PromptTemplate


from api.config import Config
from api.models.data import DataSourceInDB
from api.models.codex import AmbiguousColumns, BaseAmbiguities
from api.utilities.gpt import din_completion
from api.utilities.prompt import (
    schema_linking_prompt_maker,
    classification_prompt_maker,
    easy_prompt_maker,
    medium_prompt_maker,
    hard_prompt_maker,
    column_ambiguity_prompt_maker,
    join_type_ambiguity_prompt_maker,
    update_question_prompt_maker,
)

DATABASE_URL = Config.DATABASE_URL
OPEN_API_KEY = Config.OPEN_API_KEY


def get_din_sql(question: str, data_sources: List[DataSourceInDB]):
    prompt = schema_linking_prompt_maker(question, data_sources)
    schema_links = din_completion(prompt)
    try:
        schema_links = schema_links.split("Schema_links: ")[1]
    except BaseException:
        print("Slicing error for the schema_linking module")
        schema_links = "[]"

    #
    prompt = classification_prompt_maker(question, data_sources, schema_links[1:])
    classification = din_completion(prompt)
    print("classification:", classification)

    try:
        predicted_class = classification.split("Label: ")[1]
    except BaseException:
        print("Slicing error for the classification module")
        predicted_class = '"NESTED"'

    # Generate SQL.
    if '"EASY"' in predicted_class:
        sql_prompt = easy_prompt_maker(question, data_sources, schema_links)
        SQL = din_completion(sql_prompt)
    elif '"NON-NESTED"' in predicted_class:
        sql_prompt = medium_prompt_maker(question, data_sources, schema_links[1:])
        SQL = din_completion(sql_prompt)
        SQL = SQL.split("SQL: ")[1]
    else:
        sub_questions = classification.split('questions = ["')[1].split('"]')[0]
        sql_prompt = hard_prompt_maker(
            question, data_sources, schema_links[1:], sub_questions
        )
        SQL = din_completion(sql_prompt)
        SQL = SQL.split("SQL: ")[1]

    return SQL


def debug_agent(question: str, sql: str, data_sources: List[DataSourceInDB]) -> str:
    openai.open_api_key = OPEN_API_KEY

    tables_names = [ds.table_name for ds in data_sources]

    db = SQLDatabase.from_uri(
        DATABASE_URL,
        include_tables=tables_names,
    )
    toolkit = SQLDatabaseToolkit(
        db=db,
        llm=OpenAI(temperature=0, openai_api_key=OPEN_API_KEY),
    )

    tools = toolkit.get_tools()
    tools = [tools[0]]

    agent = initialize_agent(
        llm=OpenAI(
            temperature=0,
            openai_api_key=OPEN_API_KEY,
        ),
        tools=tools,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    prompt = PromptTemplate(
        input_variables=["question", "sql_dialect", "sql", "current_date"],
        template="""
        You are a helpful AI that verifies that a SQL query runs correctly.
        If the query does not run successfully, you will iteratelively update the query based on the error message.

        You follow the following procedure:
        1. Run the input SQL query using the QuerySQLDataBaseTool
        2. If this runs successfully, return immediately.
        3. If the SQL query fails. debug the query:
            3a. consider the error message
            3b. update the SQL query
            3c. try re-running
            3d. if the query returns an empty result [], try changing the JOIN to use a LEFT JOIN
        4. Repeat step 3 until you have a valid result. Finish and exit with the updated SQL query. The answer should be the updated SQL query. Not the result of the query.

        You are writing SQL for the {sql_dialect} dialect.
        Convert all dates the format YYYY-MM-DD. The current day is {current_date} if the user references the date.
        The user's original question: {question}
            The SQL: {sql}
        Begin!
        """,
    )

    formatted_prompt = prompt.format(
        question=question,
        sql=sql,
        sql_dialect=db.dialect,
        current_date=datetime.datetime.now().strftime("%Y-%m-%d"),
    )

    debugged_sql = agent.run(formatted_prompt)

    return debugged_sql


def update_question(question: str, statement: str, answer: str):
    prompt = update_question_prompt_maker(question, statement, answer)
    updated_question = din_completion(prompt)

    return updated_question


def remove_column_ambiguities(
    input: str, data_sources: List[DataSourceInDB]
) -> Union[AmbiguousColumns, None]:

    prompt = column_ambiguity_prompt_maker(input, data_sources)
    ambiguities = din_completion(prompt)

    print(ambiguities)

    try:
        ambiguities = ambiguities.split("Ambiguities: ")[1]
    except BaseException:
        print("Slicing error for the ambiguity module")
        ambiguities = "[]"
        return None

    if ambiguities == "None":
        return None
    else:
        term = re.findall(r'"([^"]*)"', ambiguities)
        columns = re.findall(r"\[(.*?)\]", ambiguities)
        ambigious_columns = AmbiguousColumns(
            question=input,
            statement=ambiguities,
            term=term,
            columns=columns,
        )

    return ambigious_columns


def remove_join_type_ambiguities(
    input: str, data_sources: List[DataSourceInDB]
) -> Union[BaseAmbiguities, None]:

    prompt = join_type_ambiguity_prompt_maker(input, data_sources)
    ambiguities = din_completion(prompt)

    try:
        ambiguities = ambiguities.split("Ambiguities: ")[1]
    except BaseException:
        print("Slicing error for the ambiguity module")
        ambiguities = "[]"
        return None

    if ambiguities == "None":
        return None
    else:
        term = re.findall(r'"([^"]*)"', ambiguities)
        ambigious_columns = BaseAmbiguities(
            question=input,
            statement=ambiguities,
            term=term,
        )

    return ambigious_columns
