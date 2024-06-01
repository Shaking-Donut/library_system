import json
from psycopg import Connection, Cursor, connect, Error, sql
from psycopg.rows import dict_row
from dotenv import dotenv_values
from . import schemas

if __name__ == "__main__":
    print("This file is not meant to be run directly")
    exit(1)

CONNECTION_CONFIG = {
    'dbname': dotenv_values('.env')['DB_NAME'],
    'user': dotenv_values('.env')['DB_USER'],
    'password': dotenv_values('.env')['DB_PASSWORD'],
    'port': dotenv_values('.env')['DB_PORT'],
    'host': dotenv_values('.env')['DB_HOST'],
    'autocommit': True,
    'row_factory': dict_row
}

DB_NAME = dotenv_values('.env')['DB_NAME']
DEFAULT_DB_NAME = "postgres"


def database_init(cur: Cursor, conn: Connection):
    # check if database already exists
    cur.execute("SELECT datname FROM pg_database")
    db_list = cur.fetchall()
    db_list = [db["datname"] for db in db_list]

    if DB_NAME in db_list:
        print("Error: Database already exists")

        # for development purposes, I will drop the database if it exists
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE);").format(
            sql.Identifier(DB_NAME)))
        print(f"Dev: Database {DB_NAME} dropped successfully")
        return

    # create databse if it does not exist
    cur.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(DB_NAME)))
    print(f"Database {DB_NAME} created successfully")

    # close connection to default database and connect to the new database
    print("Closing connection to default database...")
    conn.close()
    cur.close()
    print(f"Connecting to database {DB_NAME}...")
    conn = connection(DB_NAME)
    cur = conn.cursor()
    print(f"Connection to {DB_NAME} successful")

    # create a table for storing books
    cur.execute(sql.SQL("""CREATE TABLE books (
                        "id" SERIAL PRIMARY KEY, 
                        "title" VARCHAR(100), 
                        "author" VARCHAR(100), 
                        "year" INTEGER, 
                        "isbn" VARCHAR(17),
                        "branch" VARCHAR(100),
                        "is_borrowed" BOOLEAN DEFAULT FALSE,
                        "date_borrowed" DATE,
                        "borrowed_by" VARCHAR(100)
                        );"""))
    print(f"Table {DB_NAME}.books created successfully")

    # create a table for storing branches of the library
    cur.execute(sql.SQL("""CREATE TABLE branches (
                        id SERIAL PRIMARY KEY, 
                        name VARCHAR(100), 
                        location VARCHAR(100)
                        );"""))
    print(f"Table {DB_NAME}.branches created successfully")

    # create a table for storing users
    cur.execute(sql.SQL("""CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100), 
                        email VARCHAR(100), 
                        name VARCHAR(100), 
                        surname VARCHAR(100),
                        is_admin BOOLEAN DEFAULT FALSE,
                        is_disabled BOOLEAN DEFAULT FALSE,
                        date_created DATE,
                        date_updated DATE,
                        password VARCHAR(100)
                        );"""))
    print(f"Table {DB_NAME}.users created successfully")

    # populate the table with sample books data from books.json
    print(f"Populating table {DB_NAME}.books with sample data...")

    with open("/workspaces/library_system/app/sample_data/books.json", "r") as f:
        books = json.load(f)
        for book in books:
            cur.execute(sql.SQL("""INSERT INTO books (title, author, year, isbn, branch, is_borrowed, date_borrowed, borrowed_by) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""),
                        (book["title"], book["author"], book["year"], book["isbn"], book["branch"], book["is_borrowed"], book["date_borrowed"], book["borrowed_by"]))
    print(f"Sample books data inserted successfully, inserted {
          len(books)} books")

    # populate the table with sample branches data from branches.json
    print(f"Populating table {DB_NAME}.branches with sample data...")
    with open("/workspaces/library_system/app/sample_data/branches.json", "r") as f:
        branches = json.load(f)
        for branch in branches:
            cur.execute(sql.SQL("""INSERT INTO branches (name, location) 
                                VALUES (%s, %s);"""),
                        (branch["name"], branch["location"]))
    print(f"Sample branch data inserted successfully, inserted {
          len(branches)} branches")

    # populate the table with sample users data from users.json
    print(f"Populating table {DB_NAME}.users with sample data...")
    with open("/workspaces/library_system/app/sample_data/users.json", "r") as f:
        users = json.load(f)
        for user in users:
            cur.execute(sql.SQL("""INSERT INTO users (username, email, name, surname, is_admin, is_disabled, date_created, date_updated, password) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""),
                        (user["username"], user["email"], user["name"], user["surname"], user["is_admin"], user["is_disabled"], user["date_created"], user["date_updated"], user["password"]))
    print(f"Sample user data inserted successfully, inserted {
          len(users)} users")


def connection(dbname=None):
    try:
        cnx = connect(**{key: value for (key, value) in CONNECTION_CONFIG.items()
                      if key != "dbname"}, dbname=dbname if dbname else CONNECTION_CONFIG['dbname'])
    except Error as e:
        print(f"Error: {e}")
        print(f"Connecting to default database {DEFAULT_DB_NAME}...")
        cnx = connection(DEFAULT_DB_NAME)
        print(f"Connection to {DEFAULT_DB_NAME} successful")
        print(f"Initializing database {DB_NAME}...")
        database_init(conn=cnx, cur=cnx.cursor())
        print(f"Database {DB_NAME} initialized successfully")
        cnx = connection(DB_NAME)
    finally:
        return cnx


conn = connection()
cur = conn.cursor()


# Books operations -----------------------------------------


def get_books() -> list[schemas.Book]:
    cur.execute(sql.SQL("SELECT * FROM books;"))
    books = cur.fetchall()
    return books


def get_book(book_id) -> schemas.Book:
    cur.execute(sql.SQL("SELECT * FROM books WHERE id = %s;"),
                sql.Identifier(book_id))
    book = cur.fetchone()
    return book


def add_book(book: schemas.BookAdd) -> schemas.Book:
    title = book.title
    author = book.author
    year = book.year
    isbn = book.isbn
    branch = book.branch
    book_added = ""

    try:
        cur.execute(sql.SQL("""INSERT INTO books ("title", "author", "year", "isbn", "branch") 
                            VALUES (%s, %s, %s, %s, %s) RETURNING *;"""),
                    (title, author, year, isbn, branch))
        book_added = cur.fetchone()
    except Error as e:
        print(f"Error adding book: {e}")
    else:
        print(f"Book added successfully: {book_added}")
        return book_added


def delete_book(book_id) -> bool:
    try:
        cur.execute(sql.SQL("DELETE FROM books WHERE id = %s;"),
                    sql.Identifier(book_id))
    except Error as e:
        print(f"Error deleting book: {e}")
        return False
    else:
        print(f"Book id={book_id} deleted successfully")
        return True


def borrow_book(book_id, user_id) -> bool:
    try:
        cur.execute(sql.SQL(
            "UPDATE books SET is_borrowed = TRUE, borrowed_by = %s WHERE id = %s;"), (user_id, book_id))
    except Error as e:
        print(f"Error borrowing book: {e}")
        return False
    else:
        print(f"Book id={book_id} borrowed by user={user_id} successfully")
        return True


def return_book(book_id):
    try:
        cur.execute(sql.SQL(
            "UPDATE books SET is_borrowed = FALSE, borrowed_by = NULL WHERE id = %s;"), sql.Identifier(book_id))
    except Error as e:
        print(f"Error returning book: {e}")
        return False
    else:
        print(f"Book id={book_id} returned successfully")
        return True

# Branches operations -----------------------------------------

# Users operations -----------------------------------------


def get_user(user_id) -> schemas.UserInDB:
    cur.execute(sql.SQL("SELECT * FROM users WHERE id = %s;"),
                sql.Identifier(user_id))
    user = cur.fetchone()
    return user


def get_user_by_username(username) -> schemas.UserInDB:
    cur.execute(sql.SQL("SELECT * FROM users WHERE username = %s;"),
                (username,))
    user = cur.fetchone()
    return user


def is_user_admin(user_id) -> bool:
    cur.execute(sql.SQL("SELECT is_admin FROM users WHERE id = %s;"),
                sql.Identifier(user_id))
    is_admin = cur.fetchone()
    return is_admin
