from api.config import Config
from api.database.database import session
from api.database.models import UserDB
from api.models.user import TokenData, UserInDB, UserWithId

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Union

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
LOOKER_ACCESS_TOKEN = Config.LOOKER_ACCESS_TOKEN
ACCESS_TOKEN_EXPIRE_MINUTES = int(Config.ACCESS_TOKEN_EXPIRE_MINUTES)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Authentication
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    """
    Authenticates a user by checking if the provided username and password match a user in the system.

    Parameters:
        username (str): The username of the user to authenticate.
        password (str): The password of the user to authenticate.

    Returns:
        User: The authenticated user object, or False if the authentication fails.
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    Create an access token based on the provided data and expiration time.

    Parameters:
        data (dict): A dictionary containing the data to be encoded in the access token.
        expires_delta (Union[timedelta, None]): Optional. The time delta specifying the expiration time of the token. If not provided, a default expiration time of 15 minutes will be used.

    Returns:
        str: The encoded access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user based on the provided token.

    Parameters:
    - token (str): The authentication token.

    Returns:
    - User: The current user.

    Raises:
    - HTTPException: If the token is expired or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Your AirPipe token has expired or invalid. For security purposes, please login to AirPipe again: https://airpipe.onrender.com/login",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        print(e)
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_user(username: str):
    """
    Retrieves a user from the database based on the provided username.

    Parameters:
        username (str): The username of the user to retrieve.

    Returns:
        UserInDB: An instance of the UserInDB class representing the retrieved user.

    Raises:
        HTTPException: If there is an error querying the database or if the user is not found.
    """
    # Change db to get all users from database
    try:
        user = session.query(UserDB).filter(UserDB.email == username).first()
    except BaseException as e:
        print("Error in get_user", e)
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
    finally:
        session.close()
        session.remove()
    if user:
        user_dict = user.__dict__
        return UserInDB(**user_dict)
    
def get_user_with_id(username: str):
    """
    Retrieves a user with the given username from the database.

    Args:
        username (str): The username of the user.

    Returns:
        UserWithId: An instance of the UserWithId class representing the retrieved user.

    Raises:
        HTTPException: If there is an error retrieving the user from the database.
    """
    # Change db to get all users from database
    try:
        user = session.query(UserDB).filter(UserDB.email == username).first()
    except BaseException as e:
        print("Error in get_user", e)
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
    finally:
        session.close()
        session.remove()
    if user:
        user_dict = user.__dict__
        return UserWithId(**user_dict)


def validate_looker_token(token: str):
    """
    Validate Looker token.

    Args:
        token (str): The Looker access token to be validated.

    Raises:
        HTTPException: If the token is invalid.

    Returns:
        str: The validated Looker access token.
    """
    if token != LOOKER_ACCESS_TOKEN:
        raise HTTPException(status_code=400, detail="Invalid Token")

    return token
