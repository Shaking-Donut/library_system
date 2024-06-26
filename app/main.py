from typing import Union, Annotated
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values

from . import database
from . import auth
from .schemas import Book, BookAdd, Token, User, UserAdd, Branch, BranchAdd

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:62626",
    "http://localhost:*",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

JWT_EXPIRATION = int(dotenv_values(".env")["JWT_EXPIRATION"])


@app.get("/", tags=["Root"])
def read_root() -> dict[str, str]:
    return {"message": "Hello World, the API is working!"}

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


@app.post("/register/", tags=["Auth"])
def register_user(user: UserAdd) -> Token:
    user = auth.register_user(user)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists")

    access_token_expires = timedelta(seconds=JWT_EXPIRATION)
    access_token = auth.create_access_token(
        data={"sub": user.id, "username": user.username, "is_admin": user.is_admin}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/current_user/", tags=["Auth"])
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return auth.get_current_user(token)

# Book endpoints -----------------------------------------


@app.get("/books/", tags=["Books"])
def get_books(branch_id: str | None = None, search_query: str | None = None) -> list[Book]:
    books = database.get_books(branch_id, search_query=search_query)
    books.sort(key=lambda book: book['title'].lower())
    return books


@app.get("/books/me/", tags=["Books"])
def get_my_books(token: str = Depends(oauth2_scheme)) -> list[Book]:
    user = auth.get_current_user(token)
    return database.get_user_books(user.id)


@app.get("/book/{book_id}/", tags=["Books"])
def get_book(book_id: int) -> Book:
    book = database.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/book/", tags=["Books"])
def add_book(book: BookAdd, token: str = Depends(oauth2_scheme)) -> Book:
    user = auth.get_current_user(token)
    if not user.is_admin:
        raise HTTPException(
            status_code=401, detail="You are not an admin", headers={"WWW-Authenticate": "Bearer"}
        )
    return database.add_book(**book)


@app.delete("/book/{book_id}/", tags=["Books"])
def delete_book(book_id: int, token: str = Depends(oauth2_scheme)) -> bool:
    user = auth.get_current_user(token)
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail="You are not an admin", headers={"WWW-Authenticate": "Bearer"}
        )
    return database.delete_book(book_id)


@app.put("/book/{book_id}/borrow/", tags=["Books"])
def borrow_book(book_id: int, token: str = Depends(oauth2_scheme)) -> bool:
    user = auth.get_current_user(token)
    user_id = user.id
    book = database.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return database.borrow_book(book_id, user_id)


@app.put("/book/{book_id}/return/", tags=["Books"])
def return_book(book_id: int) -> bool:
    book = database.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return database.return_book(book_id)

# Branch endpoints -----------------------------------------


@app.get("/branches/", tags=["Branches"])
def get_branches() -> list[Branch]:
    return database.get_branches()


@app.get("/branch/{branch_id}/", tags=["Branches"])
def get_branch(branch_id: int) -> Branch:
    branch = database.get_branch(branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@app.post("/branch/", tags=["Branches"])
def add_branch(branch: BranchAdd, token: str = Depends(oauth2_scheme)) -> Branch:
    user = auth.get_current_user(token)
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail="You are not an admin", headers={"WWW-Authenticate": "Bearer"}
        )
    return database.add_branch(branch)


@app.delete("/branch/{branch_id}/", tags=["Branches"])
def delete_branch(branch_id: int, token: str = Depends(oauth2_scheme)) -> bool:
    user = auth.get_current_user(token)
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail="You are not an admin", headers={"WWW-Authenticate": "Bearer"}
        )
    return database.delete_branch(branch_id)
