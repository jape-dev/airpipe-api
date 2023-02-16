from typing import Union
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api import google
from api.database import session, engine, insert_new_user
from typing import List
from api import models
from api.codex import Completion
import openai
import requests
from starlette.responses import RedirectResponse
from starlette.datastructures import URL
from api.customer import User, Token, TokenData, UserInDB
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
import sqlalchemy
from api.facebook import AdAccount, FacebookQuery, FacebookQueryResults
import pandas as pd
from typing import List, Dict, Any
import os
from api.config import Config


SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(Config.ACCESS_TOKEN_EXPIRE_MINUTES)
DOMAIN_URL = Config.DOMAIN_URL
FB_CLIENT_SECRET = Config.FB_CLIENT_SECRET


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://airpipe.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Authentication
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_user(username: str):
    # Change db to get all users from database
    user = session.query(models.User).filter(models.User.email == username).first()
    if user:
        user_dict = user.__dict__
        return UserInDB(**user_dict)


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoints
@app.get("/")
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
    try:
        results = connection.execute(query)
    except sqlalchemy.exc.ProgrammingError as e:
        raise HTTPException(status_code=400, detail=str(e))

    query_results = google.QueryResults(results=results.all())

    return query_results


@app.get('/facebook_login')
def facebook_login(request: Request):
    app_id = 3796703967222950
    code = request.query_params['code']
    token = request.query_params['state']

    redirect_uri = f"{DOMAIN_URL}/facebook_login/"
    auth_url = f"https://graph.facebook.com/v15.0/oauth/access_token?client_id={app_id}&redirect_uri={redirect_uri}&code={code}&client_secret={FB_CLIENT_SECRET}"

    # Save the access token to the user's database.
    response = requests.get(auth_url)

    json = response.json()
    access_token = json['access_token']

    # Commit access_token to the database.
    user: User = get_current_user(token)

    user = session.query(models.User).filter(models.User.email == user.email).first()
    user.access_token = access_token
    session.add(user)
    session.commit()

    return RedirectResponse(url=DOMAIN_URL)


@app.post('/create_customer', response_model=User)
def create_customer(user: User):

    hashed_password = get_password_hash(user.hashed_password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    exsiting_user = session.query(models.User).filter(models.User.email == user.email).first()
    if exsiting_user:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        insert_new_user(new_user)
        return user


@app.get('/ad_accounts', response_model=List[AdAccount])
def ad_accounts(token: str):
    current_user: User = get_current_user(token)
    adaccounts = []

    url = f"https://graph.facebook.com/v15.0/me?fields=adaccounts&access_token={current_user.access_token}"
    response = requests.get(url)
    json = response.json()
    accounts = json['adaccounts']['data']

    for account in accounts:
        id = account['id']
        account_id = account['account_id']
        url = f"https://graph.facebook.com/v15.0/{id}?fields=name&access_token={current_user.access_token}"
        response = requests.get(url)
        json = response.json()
        name = json['name']

        adaccount: AdAccount = AdAccount(id=id, account_id=account_id,
                                         name=name)
        adaccounts.append(adaccount)

    return adaccounts


@app.post('/run_facebook_query', response_model=FacebookQueryResults)
def run_facebook_query(query: FacebookQuery, token: str):
    current_user: User = get_current_user(token)

    fields = query.dimensions + query.metrics
    if 'date' in fields:
        fields.remove('date')
    fields = ','.join(fields)

    # Need to add in date and actions.

    start_datetime = datetime.fromtimestamp(query.start_date)
    end_datetime = datetime.fromtimestamp(query.end_date)
    start_date = start_datetime.strftime("%Y-%m-%d")
    end_date = end_datetime.strftime("%Y-%m-%d")

    url = f"https://graph.facebook.com/v15.0/{query.account_id}/insights?level=ad&fields={fields}&time_range={{'since':'{start_date}','until':'{end_date}'}}&time_increment=1&access_token={current_user.access_token}"

    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Facebook query failed")
    json = response.json()
    data = json['data']

    for datum in data:
        # check if metric doe snot exist in the datum keys and set it to 0.
        for metric in query.metrics:
            if metric not in datum.keys():
                datum[metric] = 0

        if datum['date_start'] == datum['date_stop']:
            datum['date'] = datum['date_start']
            del datum['date_start']
            del datum['date_stop']

            if 'date' not in query.dimensions:
                del datum['date']

    return FacebookQueryResults(results=data)


@app.post('/create_new_table')
def create_new_table(results: google.CurrentResults = Body(...)):
    df = pd.DataFrame(results.results, columns=results.columns)
    df = df.apply(pd.to_numeric, errors='ignore')
    df.to_sql(results.name, engine, if_exists='replace', index=False)

    return {"message": "success"}


@app.get('/current_user', response_model=User)
def current_user(token: str):
    print("token", token)
    current_user: User = get_current_user(token)
    return current_user


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000)
