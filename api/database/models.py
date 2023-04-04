from api.database.database import Base
from sqlalchemy import String, Column, Integer


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer(), primary_key=True)
    email = Column(String(), unique=True)
    hashed_password = Column(String())
    facebook_access_token = Column(String(), nullable=True)
    google_access_token = Column(String(), nullable=True)
    access_token = Column(String(), nullable=True)
