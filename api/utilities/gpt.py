from api.config import Config
import openai
from langchain.memory import PostgresChatMessageHistory


OPEN_API_KEY = Config.OPEN_API_KEY
DATABASE_URL = Config.DATABASE_URL


def create_schema_link():
    pass


def chat_completion(prompt):

    openai.api_key = OPEN_API_KEY

    message = [{"role": "user", "content": prompt}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message,
        temperature=0,
        max_tokens=1000,
        n=1,
        frequency_penalty=0.5,
        presence_penalty=0.5,
    )

    completion = response.choices[0].message["content"]

    return completion


def din_completion(prompt):

    openai.api_key = OPEN_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        n=1,
        stream=False,
        temperature=0.0,
        max_tokens=600,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["Q:"],
    )

    return response["choices"][0]["message"]["content"]


def get_message_history(session_id: str) -> PostgresChatMessageHistory:
    history = PostgresChatMessageHistory(
        connection_string=DATABASE_URL,
        session_id=session_id,
    )

    return history
