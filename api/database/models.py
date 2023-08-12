from api.database.database import Base
from sqlalchemy import String, Column, Integer, Boolean


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer(), primary_key=True)
    email = Column(String(), unique=True)
    hashed_password = Column(String())
    onboarding_stage = Column(String())
    facebook_access_token = Column(String(), nullable=True)
    google_access_token = Column(String(), nullable=True)
    google_analytics_access_token = Column(String(), nullable=True)


class DataSourceDB(Base):
    __tablename__ = "data_sources"

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


class ConversationsDB(Base):
    __tablename__ = "conversations"

    id = Column(Integer(), primary_key=True)
    conversation_id = Column(Integer())
    user_id = Column(Integer())
    message = Column(String())
    is_user_message = Column(Boolean())
