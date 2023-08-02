from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.user import User
from api.config import Config

db_uri = Config.DATABASE_URL
engine = create_engine(db_uri, pool_size=20, max_overflow=10)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
