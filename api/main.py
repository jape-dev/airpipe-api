from api.config import Config
from api.connector import connector_router
from api.query import query_router
from api.user import user_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

SECRET_KEY = Config.SECRET_KEY

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://airpipe.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(connector_router.router)
app.include_router(query_router.router)
app.include_router(user_router.router)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
