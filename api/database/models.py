import datetime
from sqlalchemy import String, Column, Integer, Boolean, DateTime

from api.database.database import Base
from api.utilities.datetime import tzware_datetime, AwareDateTime


class UserDB(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(Integer(), primary_key=True)
    email = Column(String(), unique=True)
    hashed_password = Column(String())
    onboarding_stage = Column(String())
    facebook_access_token = Column(String(), nullable=True)
    google_access_token = Column(String(), nullable=True)
    google_analytics_access_token = Column(String(), nullable=True)
    created_at = Column(DateTime(), default=datetime.datetime.now())


class DataSourceDB(Base):
    __tablename__ = "data_sources"
    __table_args__ = {"schema": "public"}

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer())
    name = Column(String())
    db_schema = Column(String())
    table_name = Column(String())
    fields = Column(String())
    channel = Column(String())
    channel_img = Column(String())
    ad_account_id = Column(String())
    start_date = Column(String())
    end_date = Column(String())
    created_at = Column(DateTime(), default=datetime.datetime.now())


class ConversationsDB(Base):
    __tablename__ = "conversations"
    __table_args__ = {"schema": "public"}

    id = Column(Integer(), primary_key=True)
    conversation_id = Column(Integer())
    user_id = Column(Integer())
    message = Column(String())
    is_user_message = Column(Boolean())
    created_at = Column(DateTime(), default=datetime.datetime.now())
