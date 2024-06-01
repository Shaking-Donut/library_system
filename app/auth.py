from datetime import datetime, timedelta
from typing import Annotated

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
from dotenv import dotenv_values

from . import database
from . import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = dotenv_values(".env")["JWT_SECRET"]
ALGORITHM = dotenv_values(".env")["JWT_ALGORITHM"]


def transform_user(user: schemas.UserInDB) -> schemas.User:
    del user['password']
    return schemas.User(**user)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> bool | schemas.User:
    user = database.get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False

    return transform_user(user)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception: HTTPException) -> schemas.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        is_admin: bool = payload.get("is_admin")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(
            id=user_id, username=username, is_admin=is_admin)
    except InvalidTokenError:
        raise credentials_exception

    return token_data


def get_current_user(token: str) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = database.get_user(token_data.id)
    if user is None:
        raise credentials_exception

    return transform_user(user)
