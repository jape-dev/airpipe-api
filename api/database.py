from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine=create_engine("postgresql://vizo:devpassword@postgres:5432/vizo",
)

Base=declarative_base()

SessionLocal=sessionmaker(bind=engine)

session = SessionLocal()