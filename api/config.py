"""Project wide config file for shared config values"""

import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    DATABASE_URL = os.getenv("DATABASE_URL")
    DOMAIN_URL = os.getenv("DOMAIN_URL")
    CLIENT_URL = os.getenv("CLIENT_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    FB_CLIENT_SECRET = os.getenv("FB_CLIENT_SECRET")
    CLIENT_SECRETS_PATH = os.getenv("CLIENT_SECRETS_PATH")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
    GOOGLE_PROJECT_NUMBER = os.getenv("GOOGLE_PROJECT_NUMBER")
    GOOGLE_APPLICATION_CREDENTIALS_PATH = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS_PATH"
    )
    GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    OPEN_API_KEY = os.getenv("OPEN_API_KEY")
    LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    LOOKER_ACCESS_TOKEN = os.getenv("LOOKER_ACCESS_TOKEN")
    AIRBYTE_WORKSPACE_ID = os.getenv("AIRBYTE_WORKSPACE_ID")
    AIRBYTE_BASIC_TOKEN = os.getenv("AIRBYTE_BASIC_TOKEN")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_USERNAME= os.getenv("POSTGRES_USERNAME")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")