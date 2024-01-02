from fastapi import APIRouter
from typing import List, Union
from api.models.codex import CaptionData
from api.utilities.gpt import chat_completion


from api.config import Config
from api.core.codex import (
    debug_agent,
    get_din_sql,
    remove_all_ambiguities,
    update_question,
)
from api.models.codex import AmbiguousColumns, BaseAmbiguities
from api.models.data import DataSourceInDB
from api.utilities.prompt import (
    schema_linking_prompt_maker,
)
from api.utilities.gpt import din_completion


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
    

@router.post("/chart_insights", status_code=200)
def chart_insights(data: CaptionData) -> str:
    prompt = f"""You are a marketing data analyst. You have been given a table with the below data which is being visualised by a {data.chart_type} chart. 

    {data.data}
    
    Please provide three insights on the chart. Gives the insights as a numbered list. I.e. 1) First insight. 2) Second insight. 3) Third insight.

    Make sure that there is only one sentence per insight. Reference numbers from the table data.
    """

    print(prompt)
    caption = chat_completion(prompt)
    return caption