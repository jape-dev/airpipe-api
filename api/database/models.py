from api.database.database import Base
from sqlalchemy import String, Column, Integer


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer(), primary_key=True)
    email = Column(String(), unique=True)
    hashed_password = Column(String())
    facebook_access_token = Column(String(), nullable=True)
    google_access_token = Column(String(), nullable=True)


class DataSourceDB(Base):
    __tablename__ = "data_sources"

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer())
    name = Column(String())
    table_name = Column(String())
    fields = Column(String())
    channel = Column(String())
    channel_img = Column(String())
    ad_account_id = Column(String())
