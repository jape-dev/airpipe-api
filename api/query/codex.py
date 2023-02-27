from fastapi import APIRouter
from api.models.codex import Completion
from api.models.data import TableColumns, SqlQuery
import openai

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

    openai.api_key = "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"
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
def sql_query(schema: TableColumns, prompt: str):

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
        stop=["#", ";"],
    )

    query = f"SELECT {response.choices[0].text}"
    sql_query = SqlQuery(query=query)

    return sql_query
