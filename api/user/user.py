from api.database.database import session
from api.database.crud import insert_new_user, get_all_users
from api.database.models import UserDB
from api.models.user import User, UserInDB, UserWithId
from api.core.auth import get_password_hash, get_user_with_id, get_current_user
from api.core.static_data import ChannelType, OnboardingStage
from api.email.email import add_contact_to_loops, send_remind_connect_event, send_remind_data_source_event
from api.models.loops import Contact
from api.core.static_data import Environment, get_enum_member_by_value
from api.config import Config

import datetime
from fastapi import APIRouter, HTTPException

router = APIRouter()
Config.ENVIRONMENT


@router.post("/create_customer", response_model=User)
def create_customer(user: UserInDB):
    hashed_password = get_password_hash(user.hashed_password)
    new_user = UserDB(
        email=user.email,
        hashed_password=hashed_password,
        onboarding_stage=user.onboarding_stage,
        role=user.role,
        created_at=datetime.datetime.now(),
    )
    try:
        exsiting_user = session.query(UserDB).filter(UserDB.email == user.email).first()
    except BaseException as e:
        print(e)
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        session.close()
        session.remove()
    if exsiting_user:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        insert_new_user(new_user)
        env = get_enum_member_by_value(Environment, Config.ENVIRONMENT)
        loops_contact = Contact(email=user.email, environment=env)
        add_contact_to_loops(loops_contact)

        return user


@router.post("/update_onboarding_stage", response_model=User)
def update_onboarding_stage(user: User, new_stage: OnboardingStage) -> UserDB:
    try:
        existing_user = session.query(UserDB).filter(UserDB.email == user.email).first()
        if existing_user:
            existing_user.onboarding_stage = new_stage
            existing_user.onboarding_stage_updated_at = datetime.datetime.now()
            session.add(existing_user)
            session.commit()
            return user
    except BaseException as e:
        print(e)
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        session.close()
        session.remove()

    return existing_user

@router.post('/clear_access_token', response_model=User)
def clear_access_token(token: str, channel: ChannelType):
    user = get_current_user(token)
    db_uder = session.query(UserDB).filter(UserDB.email == user.email).first()

    if channel == ChannelType.google_analytics:
        db_uder.google_analytics_refresh_token = None
    elif channel == ChannelType.sheets:
        db_uder.google_sheets_refresh_token = None
    elif channel == ChannelType.youtube:
        db_uder.youtube_refresh_token = None
    else:
        db_uder.google_refresh_token = None

    # update existing user in database
    try: 
        session.add(db_uder)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Could not update access token. {e}",
        )
    finally:
        session.close()
        session.remove()

    return user
    
@router.get('/user', response_model=UserWithId)
def user(token: str) -> UserWithId:
    user = get_current_user(token)

    user_with_id = get_user_with_id(user.email)
    return user_with_id

@router.post('/loops_events')
def send_loops_events():
    users = get_all_users()
    current_datetime = datetime.now()

    for user in users:

        contact = Contact(email=user.email)

        time_delta = current_datetime - user.onboarding_stage_updated_at
        time_delta_seconds = time_delta.total_seconds()

        if time_delta_seconds > 24 * 3600 and time_delta_seconds < 48 * 3600:
            if user.onboarding_stage == OnboardingStage.signed_up:
                send_remind_connect_event(contact)
            elif user.onboarding_stage == OnboardingStage.connected:
                send_remind_data_source_event(contact)
    