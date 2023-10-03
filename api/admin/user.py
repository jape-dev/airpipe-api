from fastapi import APIRouter, HTTPException
from api.models.user import UserWithId
from api.database.crud import get_user_by_email

router = APIRouter(prefix="/user")


@router.get("/user_details", response_model=UserWithId)
def get_user(email: str) -> UserWithId:
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserWithId(**user.__dict__)
