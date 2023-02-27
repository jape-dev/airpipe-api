from api.database.database import Base
from sqlalchemy import String, Column, Integer


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer(), primary_key=True)
    email = Column(String(), unique=True)
    hashed_password = Column(String())
    access_token = Column(String(), nullable=True)
