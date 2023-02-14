"""Project wide config file for shared config values"""

import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    DB_URI = os.getenv("DATABASE_URL")
