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
    date_borrowed: datetime | None
    borrowed_by: str | None


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


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
    username: str
    is_admin: bool
