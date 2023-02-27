from api.database.database import session, insert_new_user
from api.database.models import UserDB
from api.models.user import User
from api.core.auth import get_password_hash

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/create_customer", response_model=User)
def create_customer(user: User):

    hashed_password = get_password_hash(user.hashed_password)
    new_user = UserDB(email=user.email, hashed_password=hashed_password)
    exsiting_user = session.query(UserDB).filter(UserDB.email == user.email).first()
    if exsiting_user:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        insert_new_user(new_user)
        return user
