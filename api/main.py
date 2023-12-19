from api.config import Config
from api.admin import admin_router
from api.connector import connector_router
from api.core.static_data import FieldType, ChannelType, OnboardingStage, UserRoleType
from api.query import query_router
from api.user import user_router
from api.models.data import (
    TabData,
    Schema,
    TableColumns,
    FieldOption,
    FieldOptionWithDataSourceId,
    JoinType,
    JoinCondition,
)
from api.models.conversation import Message
from api.models.user import User

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.utils import get_model_definitions
from pydantic.schema import get_model_name_map
from starlette.middleware.sessions import SessionMiddleware
from typing import Dict, Any
import uvicorn


SECRET_KEY = Config.SECRET_KEY

app = FastAPI()


def custom_openapi() -> Dict[str, Any]:
    """Make custom changes to the generated OpenAPI schema

    Returns:
        Dict[str, Any]: the OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AirPipe",
        version="0.0.1",
        description="AirPipe backend",
        routes=app.routes,
    )

    # We manually include models that aren't used in any
    # FastAPI routes here, which we still want to present in the
    # generated OpenAPI schema; this is useful
    # for the front-end to generate client-side models
    flat_models = [
        TableColumns,
        TabData,
        Schema,
        FieldType,
        FieldOption,
        ChannelType,
        Message,
        User,
        OnboardingStage,
        FieldOptionWithDataSourceId,
        JoinType,
        JoinCondition,
        UserRoleType
    ]
    model_name_map = get_model_name_map(flat_models)  # type: ignore
    definitions = get_model_definitions(
        flat_models=flat_models, model_name_map=model_name_map  # type: ignore
    )

    openapi_schema["components"]["schemas"] = {
        **openapi_schema["components"]["schemas"],
        **definitions,
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://airpipe.onrender.com",
    "https://api-airpipe.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(admin_router.router)
app.include_router(connector_router.router)
app.include_router(query_router.router)
app.include_router(user_router.router)

templates = Jinja2Templates(directory="api/templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        "google1d76773c48148b4b.html", {"request": request}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
