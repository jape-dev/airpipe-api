from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api import google
from api.database import session, engine
import sqlalchemy as db
from typing import List
from api import models
from api.codex import Completion
import openai


app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hello_world")
def hello_world():
    return "Hello World"


@app.get("/codex", response_model=Completion, response_description="Code completion response from codex")
def codex(prompt: str, completion: str = None):

    base = "<|endoftext|>/* I start with a blank HTML page, and incrementally modify it via <script> injection. Written for Chrome. */\n/* Command: Add \"Hello World\", by adding an HTML DOM node */\nvar helloWorld = document.createElement('div');\nhelloWorld.innerHTML = 'Hello World';\ndocument.body.appendChild(helloWorld);\n/* Command: Clear the page. */\nwhile (document.body.firstChild) {\n  document.body.removeChild(document.body.firstChild);\n}\nvar script = document.createElement('script');\nscript.src = 'https://cdn.jsdelivr.net/npm/chart.js@2.9.3';\ndocument.body.appendChild(script);\n\n"

    if completion:
        new_line = completion + "\n/* " + f"Command: {prompt} */\n"
    else:
        new_line = "/* " + f"Command: {prompt} */\n"

    prompt = base + new_line

    openai.api_key = "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"
    response = openai.Completion.create(
        model="code-davinci-002",
        prompt=prompt,
        max_tokens=1000,
        temperature=0,
        stop="/* Command:"
    )

    completed_code = prompt + response.choices[0].text
    completed_code = completed_code.replace('<|endoftext|>', '')

    completion = Completion(completion=completed_code)

    return completion


@app.get('/ads', response_model=List[google.GoogleAd], status_code=200)
def get_all_google_ads():
    ads = session.query(models.GoogleAd).all()

    return ads


@app.get('/table_columns', response_model=google.TableColumns, status_code=200)
def get_table_columns(table_name: str):
    connection = engine.connect()
    result = connection.execute(f"SELECT * FROM {table_name} LIMIT 1")
    cols = [col for col in result.keys()]
    table_columns = google.TableColumns(name=table_name, columns=cols)

    return table_columns


@app.post('/sql_query', response_model=google.SqlQuery, status_code=200)
def sql_query(schema: google.TableColumns, prompt: str):

    prompt = f"### Postgres SQL tables, with their properties: \n#\n# {schema.name}({','.join(schema.columns)}) \n#\n### {prompt}\nSELECT"
    openai.api_key = "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"

    response = openai.Completion.create(
        model="code-davinci-002",
        prompt=prompt,
        temperature=0,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["#", ";"]
    )

    query = f"SELECT {response.choices[0].text}"
    sql_query = google.SqlQuery(query=query)

    return sql_query


@app.get('/run_query', response_model=google.QueryResults, status_code=200)
def run_query(query: str):
    connection = engine.connect()
    results = connection.execute(query)
    query_results = google.QueryResults(results=results.all())

    return query_results


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000)
