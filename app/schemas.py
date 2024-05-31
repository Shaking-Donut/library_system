from pydantic import BaseModel

from datetime import datetime


class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    isbn: str
    branch: str
    is_borrowed: bool = False
    date_borrowed: datetime
    borrowed_by: str


class BookAdd(BaseModel):
    title: str
    author: str
    year: int
    isbn: str
    branch: str


class User(BaseModel):
    id: int
    username: str
    email: str
    name: str
    surname: str
    is_admin: bool = False
    is_disabled: bool = False
    date_created: datetime
    date_updated: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int
    is_admin: bool


class UserInDB(User):
    hashed_password: str
