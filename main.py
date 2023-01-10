from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import openai
import google
# from database import SessionLocal
from typing import Optional,List
import models
from codex import Completion
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


app = FastAPI()
engine=create_engine("postgresql://vizo:devpassword@postgres:5432/vizo",
    echo=True
)

Base=declarative_base()

SessionLocal=sessionmaker(bind=engine)

db=SessionLocal()


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
    ads = db.query(models.GoogleAd).all()

    return ads


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000)
