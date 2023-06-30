import pandas as pd
import time

from api.core.data import load_postgresql_table
from api.utilities.gpt import din_completion
from api.utilities.din import (
    schema_linking_prompt_maker,
    classification_prompt_maker,
    easy_prompt_maker,
    medium_prompt_maker,
    hard_prompt_maker,
)


def get_din_sql(question: str, table: str):
    val_df = load_postgresql_table()
    # if index < 405: continue #for testing
    print(question)
    schema_links = None
    while schema_links is None:
        try:
            schema_links = din_completion(
                schema_linking_prompt_maker(question, row["db_id"])
            )
        except:
            time.sleep(3)
            pass
    try:
        schema_links = schema_links.split("Schema_links: ")[1]
    except:
        print("Slicing error for the schema_linking module")
        schema_links = "[]"
    # print(schema_links)
    classification = None
    while classification is None:
        try:
            classification = din_completion(
                classification_prompt_maker(question, row["db_id"], schema_links[1:])
            )
        except:
            time.sleep(3)
            pass
    try:
        predicted_class = classification.split("Label: ")[1]
    except:
        print("Slicing error for the classification module")
        predicted_class = '"NESTED"'
    # print(classification)
    if '"EASY"' in predicted_class:
        print("EASY")
        SQL = None
        while SQL is None:
            try:
                SQL = din_completion(
                    easy_prompt_maker(question, row["db_id"], schema_links)
                )
            except:
                time.sleep(3)
                pass
    elif '"NON-NESTED"' in predicted_class:
        print("NON-NESTED")
        SQL = None
        while SQL is None:
            try:
                SQL = din_completion(
                    medium_prompt_maker(question, row["db_id"], schema_links)
                )
            except:
                time.sleep(3)
                pass
        try:
            SQL = SQL.split("SQL: ")[1]
        except:
            print("SQL slicing error")
            SQL = "SELECT"
    else:
        sub_questions = classification.split('questions = ["')[1].split('"]')[0]
        print("NESTED")
        SQL = None
        while SQL is None:
            try:
                SQL = din_completion(
                    hard_prompt_maker(
                        question, row["db_id"], schema_links, sub_questions
                    )
                )
            except:
                time.sleep(3)
                pass
        try:
            SQL = SQL.split("SQL: ")[1]
        except:
            print("SQL slicing error")
            SQL = "SELECT"

    return SQL
