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

class Book_add(BaseModel):
    title: str
    author: str
    year: int
    isbn: str
    branch: str
