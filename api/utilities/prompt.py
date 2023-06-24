import ast
from typing import List


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


def get_ambiguity_prompt(table_info, dialect, input):
    prompt = f"""
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


def extract_columns(completion: str) -> List[str]:
    columns = completion.split("Columns: ")[1]
    columns = ast.literal_eval(columns)

    return columns
