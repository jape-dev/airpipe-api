import ast
from typing import List

from api.core.static_data import ChannelType
from api.models.data import DataSource, DataSourceInDB
from api.utilities.data import get_table_schema
from api.utilities.din import (
    schema_linking_prompt,
    classification_prompt,
    easy_prompt,
    medium_prompt,
    hard_prompt,
    column_ambiguity_prompt,
    update_question_prompt,
    join_type_ambiguity_prompt,
)


def get_missing_column_prompt(table_info, dialect, input):
    prompt = f"""
    The following are {dialect} tables and a summary of data:

    {table_info}

    The user has supplied an input question: "{input}"

    First, if all the potential columns mentioned in the input question are in the tables, return an empty list:

    Columns: []

    Otherwise, if a potential column mentioned in the input question is not in any of the tables, provide a list of alternative columns that are similar to the potential column name.
    Only include columns that exist in the tables. Use the following format:

    Columns: "Python list of strings"

    """
    return prompt


def get_ambiguity_prompt(
    table_info,
    dialect,
    input,
):
    prompt = f"""
    You are a helpful AI that verifies that a SQL query runs correctly.

    Given the following tables based on the dialect {dialect}:

    {table_info}

    The user has supplied an input question: "{input}"

    If a column name mentioned in the input question is ambiguous with another column in any of the tables, provide a list of all the ambiguous columns.
    Use the following format:

    Columns: "Python list of strings"

    If there are no ambiguous columns mentioned in the input question, return an empty list:

    Columns: []

    """
    return prompt


def clarification_prompt_maker(table_info, input, schema_links):
    prompt = f"""
    You are a helpful AI data analyst that guides the user to refine their question based on available
    tables and columns:

    {table_info}

    and schema_links: {schema_links}

    The user's original question: "{input}".

    Given the user's original question, ask the user to clairfy what they mean
    in order to select the right schema_link. This includes any ambiguous column names.

    Return the question in the format:

    Clarification: clarification question here

    If it is already clear what the schema_link needs to be used. Just return 
    Clarification: complete

    """
    return prompt


def extract_columns(completion: str) -> List[str]:
    columns = completion.split("Columns: ")[1]
    columns = ast.literal_eval(columns)

    return columns


def get_table_info(tables: List[DataSourceInDB]) -> str:
    """
    Get the table schema

    Args:
        table_name (str): The name of the table

    Returns:
        str: The table schema

    """
    table_info = ""
    for table in tables:
        table_name = table.table_name
        columns = get_table_schema(table_name)
        table_line = f"Table {table_name}, columns = [*, {', '.join(columns)}]\n"
        table_info += table_line
    return table_info


def get_foreign_keys(tables: List[DataSourceInDB]) -> str:
    facebook_fields = []
    google_fields = []
    # get all the columns from each table.
    # Need to use the field list here.
    if len(tables) > 1:
        for table in tables:
            channel = table.channel
            fields = table.fields
            fields = fields.split(",")
            for field in fields:
                if field in ["date", "segments.date"]:
                    if channel == "facebook":
                        table_field = f"{table.table_name}.{field}"
                        facebook_fields.append(table_field)
                    elif channel == "google":
                        field = field.split(".")[-1]
                        table_field = f"{table.table_name}.{field}"
                        google_fields.append(table_field)

    # Create a string for foreign keys facebook.fields == google.fields
    if len(facebook_fields) > 0 and len(google_fields) > 0:
        return f"[{facebook_fields[0]} == {google_fields[0]}]"
    else:
        return "[]"


def schema_linking_prompt_maker(question: str, data_sources: List[DataSourceInDB]):
    """
    Generates a prompt for schema linking based on a question, table name, and data sources.

    Args:
        question (str): The question for which the schema linking prompt is generated.
        table_name (str): The name of the table.
        data_sources (List[DataSource]): A list of data sources.

    Returns:
        str: The generated prompt for schema linking.

    """
    instruction = "# Find the schema_links for generating SQL queries for each question based on the database schema and Foreign keys.\n"
    fields = get_table_info(data_sources)
    foreign_keys = "Foreign_keys = " + get_foreign_keys(data_sources) + "\n"
    prompt = (
        instruction
        + schema_linking_prompt
        + fields
        + foreign_keys
        + 'Q: "'
        + question
        + """"\nA: Let’s think step by step."""
    )

    return prompt


def classification_prompt_maker(
    question: str,
    data_sources: List[DataSourceInDB],
    schema_links: str,
):
    instruction = "# For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN.\n"
    instruction += "\nif need nested queries: predict NESTED\n"
    instruction += "elif need JOIN and don't need nested queries: predict NON-NESTED\n"
    instruction += (
        "elif don't need JOIN and don't need nested queries: predict EASY\n\n"
    )
    fields = get_table_info(data_sources)
    fields += "Foreign_keys = " + get_foreign_keys(data_sources) + "\n"
    fields += "\n"
    prompt = (
        instruction
        + fields
        + classification_prompt
        + 'Q: "'
        + question
        + "\nschema_links: "
        + schema_links
        + "\nA: Let’s think step by step."
    )

    return prompt


def hard_prompt_maker(
    question: str,
    data_sources: List[DataSourceInDB],
    schema_links: str,
    sub_questions: str,
):
    instruction = "# Use the intermediate representation and the schema links to generate the SQL queries for each of the questions.\n"
    fields = get_table_info(data_sources)
    fields += "Foreign_keys = " + get_foreign_keys(data_sources) + "\n"
    stepping = f"""\nA: Let's think step by step. "{question}" can be solved by knowing the answer to the following sub-question "{sub_questions}"."""
    fields += "\n"
    prompt = (
        instruction
        + fields
        + hard_prompt
        + 'Q: "'
        + question
        + '"'
        + "\nschema_links: "
        + schema_links
        + stepping
        + '\nThe SQL query for the sub-question"'
    )

    return prompt


def medium_prompt_maker(
    question: str,
    data_sources: List[DataSourceInDB],
    schema_links: str,
):
    instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
    fields = get_table_info(data_sources)
    fields += "Foreign_keys = " + get_foreign_keys(data_sources) + "\n"
    fields += "\n"
    prompt = (
        instruction
        + fields
        + medium_prompt
        + 'Q: "'
        + question
        + "\nSchema_links: "
        + schema_links
        + "\nA: Let’s think step by step."
    )

    return prompt


def easy_prompt_maker(
    question: str, data_sources: List[DataSourceInDB], schema_links: str
):
    instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
    fields = get_table_info(data_sources)
    fields += "\n"
    prompt = (
        instruction
        + fields
        + easy_prompt
        + 'Q: "'
        + question
        + "\nSchema_links: "
        + schema_links
        + "\nSQL:"
    )

    return prompt


def column_ambiguity_prompt_maker(question: str, data_sources: List[DataSourceInDB]):
    """
    Generates a prompt for schema linking based on a question, table name, and data sources.

    Args:
        question (str): The question for which the schema linking prompt is generated.
        data_sources (List[DataSource]): A list of data sources.

    Returns:
        str: The generated prompt for ambiguous columns.

    """
    instruction = (
        "# Find the ambiguities in column names for generating SQL queries for each question based on the database schema and Foreign keys.\n If ambiguities found, return Ambiguities: ambigious column names. Otherwise return Ambiguities: None "
        ""
    )
    fields = get_table_info(data_sources)
    foreign_keys = "Foreign_keys = " + get_foreign_keys(data_sources) + "\n"
    prompt = (
        instruction
        + column_ambiguity_prompt
        + fields
        + foreign_keys
        + 'Q: "'
        + question
        + """"\nA: Let’s think step by step."""
    )

    return prompt


def join_type_ambiguity_prompt_maker(question: str, data_sources: List[DataSourceInDB]):
    """
    Generates a prompt for schema linking based on a question, table name, and data sources.

    Args:
        question (str): The question for which the schema linking prompt is generated.
        data_sources (List[DataSource]): A list of data sources.

    Returns:
        str: The generated prompt for join type ambiguiites

    """
    instruction = (
        "# Find the ambiguities in column names for generating SQL queries for each question based on the database schema and Foreign keys.\n If ambiguities found, return Ambiguities: ambigious column names. Otherwise return Ambiguities: "
        ""
    )
    fields = get_table_info(data_sources)
    foreign_keys = "Foreign_keys = " + get_foreign_keys(data_sources) + "\n"
    prompt = (
        instruction
        + join_type_ambiguity_prompt
        + fields
        + foreign_keys
        + 'Q: "'
        + question
        + """"\nA: Let’s think step by step."""
    )

    return prompt


def generic_ambiguity_prompt_makler(table_info, schema_links):
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

    return template


def update_question_prompt_maker(question: str, statement: str, answer: str):
    prompt = f"""
    {update_question_prompt}

    You are a helpful AI data analyst who is helping to make a user's question less
    ambiguous.

    Given the original question: {question}

    And the AI's clarification question: {statement}

    To which the user responsed with: {answer}

    Update the original question based on the user's response in the format
    Question: updated question

    """

    return prompt
