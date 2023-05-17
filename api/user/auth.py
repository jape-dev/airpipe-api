from api.config import Config
from api.core.auth import authenticate_user, create_access_token, get_current_user
from api.models.user import User, Token
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status

ACCESS_TOKEN_EXPIRE_MINUTES = int(Config.ACCESS_TOKEN_EXPIRE_MINUTES)

router = APIRouter(prefix="/auth")


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to login. Please try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/current_user", response_model=User)
def current_user(token: str):
    current_user: User = get_current_user(token)
    return current_user
