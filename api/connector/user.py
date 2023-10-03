from fastapi import APIRouter, HTTPException
from api.models.user import User
from api.database.crud import get_user_by_email

router = APIRouter(prefix="/user")


@router.get("/user_details", response_model=User)
def get_user(email: str) -> User:
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
