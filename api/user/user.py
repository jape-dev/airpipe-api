from api.database.database import session
from api.database.crud import insert_new_user
from api.database.models import UserDB
from api.models.user import User
from api.core.auth import get_password_hash

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/create_customer", response_model=User)
def create_customer(user: User):
    hashed_password = get_password_hash(user.hashed_password)
    new_user = UserDB(
        email=user.email,
        hashed_password=hashed_password,
        onboarding_stage=user.onboarding_stage,
    )
    try:
        session.connection(
            execution_options={"schema_translation_map": {None: "public"}}
        )
        exsiting_user = session.query(UserDB).filter(UserDB.email == user.email).first()
    except BaseException as e:
        print(e)
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        session.close()
    if exsiting_user:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        insert_new_user(new_user)
        return user


@router.post("/update_onboarding_stage", response_model=User)
def update_onboarding_stage(user: User):
    try:
        exsiting_user = session.query(UserDB).filter(UserDB.email == user.email).first()
    except BaseException as e:
        print(e)
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        session.close()
    if exsiting_user:
        exsiting_user.onboarding_stage = user.onboarding_stage
        session.commit()
        return user
