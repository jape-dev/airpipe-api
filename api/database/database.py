
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker,scoped_session
from api.models.user import User
from api.config import Config

db_uri = Config.DATABASE_URL
engine = create_engine(
    db_uri,
    pool_size=20,
    max_overflow=10,
    pool_recycle=300,
    pool_pre_ping=True,
    pool_use_lifo=True,
)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

session = scoped_session(SessionLocal)
