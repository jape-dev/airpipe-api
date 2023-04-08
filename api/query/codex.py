from fastapi import APIRouter
import openai
from typing import Optional

from api.config import Config
from api.models.codex import Completion
from api.models.data import DebugResponse, SqlQuery, Schema

OPEN_API_KEY = Config.OPEN_API_KEY


router = APIRouter()


@router.get(
    "/codex",
    response_model=Completion,
    response_description="Code completion response from codex",
)
def codex(prompt: str, completion: str = None):

    base = "<|endoftext|>/* I start with a blank HTML page, and incrementally modify it via <script> injection. Written for Chrome. */\n/* Command: Add \"Hello World\", by adding an HTML DOM node */\nvar helloWorld = document.createElement('div');\nhelloWorld.innerHTML = 'Hello World';\ndocument.body.appendChild(helloWorld);\n/* Command: Clear the page. */\nwhile (document.body.firstChild) {\n  document.body.removeChild(document.body.firstChild);\n}\nvar script = document.createElement('script');\nscript.src = 'https://cdn.jsdelivr.net/npm/chart.js@2.9.3';\ndocument.body.appendChild(script);\n\n"

    if completion:
        new_line = completion + "\n/* " + f"Command: {prompt} */\n"
    else:
        new_line = "/* " + f"Command: {prompt} */\n"

    prompt = base + new_line

    openai.api_key = OPEN_API_KEY
    response = openai.Completion.create(
        model="code-davinci-002",
        prompt=prompt,
        max_tokens=1000,
        temperature=0,
        stop="/* Command:",
    )

    completed_code = prompt + response.choices[0].text
    completed_code = completed_code.replace("<|endoftext|>", "")

    completion = Completion(completion=completed_code)

    return completion


@router.post("/sql_query", response_model=SqlQuery, status_code=200)
def sql_query(schema: Schema, prompt: str):

    schema_string = ""
    for tab in schema.tabs:
        data = tab.data[-1]
        schema_string += f"\n# {data.name}({','.join(data.columns)})"
    prompt = f"### Postgres SQL tables, with their properties: \n#{schema_string} \n#\n### {prompt}\nSELECT"
    message = [{"role": "user", "content": prompt}]

    openai.api_key = OPEN_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message,
        temperature=0,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["#", ";"],
    )

    generated_query = response.choices[0].message["content"]

    if generated_query[0:6] == "SELECT":
        query = generated_query
    elif generated_query[0:5] == "ALTER":
        query = generated_query
    else:
        query = f"SELECT {generated_query}"

    sql_query = SqlQuery(query=query)

    return sql_query


@router.post("/debug_prompt", response_model=DebugResponse, status_code=200)
def debug_prompt(schema: Schema, query: str, error: str, prompt: Optional[str] = None):
    schema_string = ""
    for tab in schema.tabs:
        data = tab.data[-1]
        schema_string += f"\n# {data.name}({','.join(data.columns)})"
    if prompt:
        instruction = f"""For a given set of Postgres SQL tables, with their properties: \n{schema_string}. \nThe following prompt {prompt} 
        produced the following query: {query}.\n This resulted in the error: {error}.\n
        Write an updated query that would , but without the error.
        """
    else:
        instruction = f"""For a given set of Postgres SQL tables, with their properties: \n{schema_string}. \nThe following query: {query} 
        produced the following error: {error}.\n
        Write an updated query that would produce the same results as the original query, but without the error.
        """
    message = [{"role": "user", "content": instruction}]

    openai.api_key = OPEN_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message,
        temperature=0,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["#", ";"],
    )

    response = DebugResponse(
        prompt=prompt,
        query=query,
        error=error,
        completion=response.choices[0].message["content"],
    )

    return response
