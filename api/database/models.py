import datetime
from sqlalchemy import String, Column, Integer, Boolean, DateTime, Date

from api.database.database import Base


class UserDB(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(Integer(), primary_key=True)
    email = Column(String(), unique=True)
    hashed_password = Column(String())
    onboarding_stage = Column(String())
    role = Column(String(), nullable=True)
    facebook_access_token = Column(String(), nullable=True)
    google_refresh_token = Column(String(), nullable=True)
    google_analytics_refresh_token = Column(String(), nullable=True)
    google_sheets_refresh_token = Column(String(), nullable=True)
    youtube_refresh_token = Column(String(), nullable=True)
    instagram_access_token = Column(String(), nullable=True)
    created_at = Column(DateTime())
    onboarding_stage_updated_at = Column(DateTime(), nullable=True)
    airbyte_destination_id = Column(String(), nullable=True)



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
    ad_account_name = Column(String(), nullable=True)
    start_date = Column(DateTime())
    end_date = Column(DateTime())
    dh_connection_id = Column(String(), nullable=True)
    airbyte_source_id = Column(String(), nullable=True)
    airbyte_connection_id = Column(String(), nullable=True)
    load_completed = Column(Boolean(), nullable=True, default=False)

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


class ViewDB(Base):
    __tablename__ = "views"
    __table_args__ = {"schema": "public"}

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer())
    name = Column(String())
    db_schema = Column(String())
    table_name = Column(String())
    fields = Column(String())
    dh_connection_id = Column(String(), nullable=True)
    start_date = Column(DateTime(), nullable=True)
    end_date = Column(DateTime(), nullable=True)
    created_at = Column(DateTime(), default=datetime.datetime.now())


class JoinConditionDB(Base):
    __tablename__ = "join_conditions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer(), primary_key=True)
    condition_id = Column(Integer())
    view_id = Column(Integer())
    left_data_source_id = Column(Integer())
    right_data_source_id = Column(Integer())
    left_field = Column(String())
    right_field = Column(String())
    join_type = Column(String())
    created_at = Column(DateTime(), default=datetime.datetime.now())


class ChartDB(Base):
    __tablename__ = "charts"
    __table_args__ = {"schema": "public"}

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer())
    chart_id = Column(String(), unique=True)
    chart_type = Column(String())
    selected_dimension = Column(String())
    selected_metric = Column(String())
    primary_color = Column(String())
    secondary_color = Column(String())
    slice_colors = Column(String())
    title=Column(String())
    caption=Column(String())
