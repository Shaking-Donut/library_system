from typing import Union

from fastapi import FastAPI
from . import database
from .schemas import Book, Book_add

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/login")
def login_user(login: str, password: str):
    return login and password

# Book endpoints -----------------------------------------

@app.get("/books/")
def get_books() -> list[Book]:
    return database.get_books()

@app.get("/book/{book_id}/")
def get_book(book_id: int) -> Book:
    return database.get_book(book_id)

@app.post("/book/")
def add_book(book: Book_add) -> Book:
    return database.add_book(**book)

@app.delete("/book/{book_id}/")
def delete_book(book_id: int) -> bool:
    return database.delete_book(book_id)

@app.put("/book/{book_id}/borrow/{user_id}/")
def borrow_book(book_id: int, user_id: int) -> bool:
    return database.borrow_book(book_id, user_id)