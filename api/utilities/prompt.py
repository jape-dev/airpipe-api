import ast
from typing import List


from api.core.static_data import ForeignKeys, ChannelType
from api.models.data import DataSourceInDB, DataSource
from api.utilities.data import get_table_schema


schema_linking_prompt = '''
Foreign_keys = [course.dept_name = department.dept_name,instructor.dept_name = department.dept_name,section.building = classroom.building,section.room_number = classroom.room_number,section.course_id = course.course_id,teaches.ID = instructor.ID,teaches.course_id = section.course_id,teaches.sec_id = section.sec_id,teaches.semester = section.semester,teaches.year = section.year,student.dept_name = department.dept_name,takes.ID = student.ID,takes.course_id = section.course_id,takes.sec_id = section.sec_id,takes.semester = section.semester,takes.year = section.year,advisor.s_ID = student.ID,advisor.i_ID = instructor.ID,prereq.prereq_id = course.course_id,prereq.course_id = course.course_id]
Q: "Find the buildings which have rooms with capacity more than 50."
A: Let’s think step by step. In the question "Find the buildings which have rooms with capacity more than 50.", we are asked:
"the buildings which have rooms" so we need column = [classroom.capacity]
"rooms with capacity" so we need column = [classroom.building]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [50]. So the Schema_links are:
Schema_links: [classroom.building,classroom.capacity,50]
'''



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


def get_table_info(table_name: str) -> str:
    """
    Get the table schema

    Args:
        table_name (str): The name of the table 

    Returns:
        str: The table schema

    """
    columns = get_table_schema(table_name)
    return f"Table {table_name}, columns = [*, {', '.join(columns)}]"


def get_foreign_keys(tables: List[DataSource]) -> str:

    facebook_fields = []
    google_fields = []
    # get all the columns from each table.
    if len(tables) > 1:
        for table in tables:
            channel = table.adAccount.channel
            fields = table.fields
            for field in fields:
                if field.label == "Date":
                    if channel == ChannelType.facebook:
                        facebook_fields.append(field.value)
                    elif channel == ChannelType.google:
                        google_fields.append(field.value)

    # Create a string for foreign keys facebook.fields == google.fields
    if len(facebook_fields) > 0 and len(google_fields) > 0:
        return f"[{facebook_fields[0]} == {google_fields[0]}]"
    else:
        return None
