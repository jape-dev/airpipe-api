"""Project wide config file for shared config values"""

import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    DATABASE_URL = os.getenv("DATABASE_URL")
    DOMAIN_URL = os.getenv("DOMAIN_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    FB_CLIENT_SECRET = os.getenv("FB_CLIENT_SECRET")
