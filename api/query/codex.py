from fastapi import APIRouter
import openai
from typing import List, Union

from langchain import PromptTemplate, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.chains import SQLDatabaseChain

from api.config import Config
from api.core.codex import (
    debug_agent,
    get_din_sql,
    remove_all_ambiguities,
    update_question,
)
from api.models.codex import Prompt, ChainResult, AmbiguousColumns, BaseAmbiguities
from api.models.data import DataSourceInDB
from api.database.database import engine
from api.utilities.gpt import get_message_history
from api.utilities.string import remove_decimal
from api.utilities.data import tuples_to_recharts_dict
from api.utilities.prompt import (
    get_missing_column_prompt,
    get_ambiguity_prompt,
    extract_columns,
    schema_linking_prompt_maker,
)
from api.utilities.gpt import chat_completion, din_completion


OPEN_API_KEY = Config.OPEN_API_KEY
DATABASE_URL = Config.DATABASE_URL


router = APIRouter()


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


@router.post(
    "/check_ambiguous_columns",
    status_code=200,
)
def check_ambiguous_columns(
    input: str,
    data_sources: List[DataSourceInDB],
    ambiguities: Union[AmbiguousColumns, BaseAmbiguities] = None,
) -> Union[AmbiguousColumns, BaseAmbiguities, str]:
    if ambiguities is not None:
        input = update_question(ambiguities.question, ambiguities.statement, input)
        ambiguities = remove_all_ambiguities(input, data_sources)
    else:
        ambiguities = remove_all_ambiguities(input, data_sources)

    if ambiguities:
        return ambiguities
    else:
        return input
