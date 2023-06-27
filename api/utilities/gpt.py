from api.config import Config
import openai

OPEN_API_KEY = Config.OPEN_API_KEY


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
