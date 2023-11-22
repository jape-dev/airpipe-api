from fastapi import APIRouter, HTTPException, Depends
from api.models.user import UserWithId, User
from api.database.crud import get_user_by_email
from api.core.auth import get_current_user

router = APIRouter(prefix="/user")


# @router.get("/user_details", response_model=UserWithId)
# def get_user(email: str, user: User = Depends(get_current_user)) -> UserWithId:
#     user = get_user_by_email(
#         email,
#     )

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     userWith = UserWithId(**user.__dict__)

#     return userWith
