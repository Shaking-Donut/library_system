from typing import Union, Annotated
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import dotenv_values

from . import database
from . import auth
from .schemas import Book, BookAdd, Token

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

JWT_EXPIRATION = int(dotenv_values(".env")["JWT_EXPIRATION"])

# Auth endpoints -----------------------------------------


@app.post("/login/", tags=["Auth"])
async def login_to_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(seconds=JWT_EXPIRATION)
    access_token = auth.create_access_token(
        data={"sub": user.id, "username": user.username, "is_admin": user.is_admin}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# Book endpoints -----------------------------------------

@app.get("/books/me/", tags=["Books"])
async def get_my_books(token: str = Depends(oauth2_scheme)) -> list[Book]:
    user = auth.get_current_user(token)
    return database.get_user_books(user.id)


@app.get("/books/", tags=["Books"])
def get_books() -> list[Book]:
    return database.get_books()


@app.get("/book/{book_id}/", tags=["Books"])
def get_book(book_id: int) -> Book:
    return database.get_book(book_id)


@app.post("/book/", tags=["Books"])
def add_book(book: BookAdd) -> Book:
    return database.add_book(**book)


@app.delete("/book/{book_id}/", tags=["Books"])
def delete_book(book_id: int) -> bool:
    return database.delete_book(book_id)


@app.put("/book/{book_id}/borrow/", tags=["Books"])
def borrow_book(book_id: int, user_id: int) -> bool:
    return database.borrow_book(book_id, user_id)


@app.put("/book/{book_id}/return/", tags=["Books"])
def return_book(book_id: int) -> bool:
    return database.return_book(book_id)
