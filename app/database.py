import json

from psycopg import Connection, Cursor, connect, Error, sql
from datetime import datetime
from psycopg.rows import dict_row
from dotenv import dotenv_values

from . import schemas

if __name__ == "__main__":
    print(f"{__name__}: This file is not meant to be run directly")
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


def database_init(cur: Cursor, conn: Connection) -> None:
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
                        "branch" INTEGER,
                        "is_borrowed" BOOLEAN DEFAULT FALSE,
                        "date_borrowed" DATE,
                        "borrowed_by" INTEGER DEFAULT NULL
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
                        username VARCHAR(100) UNIQUE,
                        email VARCHAR(100) UNIQUE, 
                        name VARCHAR(100), 
                        surname VARCHAR(100),
                        is_admin BOOLEAN DEFAULT FALSE,
                        is_disabled BOOLEAN DEFAULT FALSE,
                        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        password VARCHAR(100)
                        );"""))
    print(f"Table {DB_NAME}.users created successfully")

    # create a trigger for updating date_updated column in users table
    print(f"Creating trigger for updating date_updated in {DB_NAME}.users...")
    cur.execute(sql.SQL("""CREATE OR REPLACE FUNCTION update_date_updated_column()
                        RETURNS TRIGGER AS $$
                        BEGIN
                            NEW.date_updated = NOW();
                            RETURN NEW;
                        END;
                        $$ language 'plpgsql';"""))
    cur.execute(sql.SQL("""CREATE TRIGGER update_date_updated_trigger
                        BEFORE UPDATE ON users
                        FOR EACH ROW
                        EXECUTE FUNCTION update_date_updated_column();"""))
    print(f"Trigger created successfully")

    # create relations books - branches and book - users
    print(f"""Creating relations between tables {
          DB_NAME}.books - {DB_NAME}.branches and {DB_NAME}.books - {DB_NAME}.users...""")
    cur.execute(sql.SQL(
        "ALTER TABLE books ADD CONSTRAINT fk_branch FOREIGN KEY(branch) REFERENCES branches(id);"))
    cur.execute(sql.SQL(
        "ALTER TABLE books ADD CONSTRAINT fk_borrowed_by FOREIGN KEY(borrowed_by) REFERENCES users(id);"))
    print(f"Relations created successfully")

    # populate the table with sample branches data from branches.json
    print(f"Populating table {DB_NAME}.branches with sample data...")
    with open("/code/app/sample_data/branches.json", "r") as f:
        branches = json.load(f)
        for branch in branches:
            cur.execute(sql.SQL("""INSERT INTO branches (name, location) 
                                VALUES (%s, %s);"""),
                        (branch["name"], branch["location"]))
    print(f"Sample branch data inserted successfully, inserted {
          len(branches)} branches")

    # populate the table with sample users data from users.json
    print(f"Populating table {DB_NAME}.users with sample data...")
    with open("/code/app/sample_data/users.json", "r") as f:
        users = json.load(f)
        for user in users:
            cur.execute(sql.SQL("""INSERT INTO users (username, email, name, surname, is_admin, is_disabled, password) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s);"""),
                        (user["username"], user["email"], user["name"], user["surname"], user["is_admin"], user["is_disabled"], user["password"]))
    print(f"Sample user data inserted successfully, inserted {
          len(users)} users")

    # populate the table with sample books data from books.json
    print(f"Populating table {DB_NAME}.books with sample data...")
    with open("/code/app/sample_data/books.json", "r") as f:
        books = json.load(f)
        for book in books:
            cur.execute(sql.SQL("""INSERT INTO books (title, author, year, isbn, branch, is_borrowed, date_borrowed, borrowed_by) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""),
                        (book["title"], book["author"], book["year"], book["isbn"], book["branch"], book["is_borrowed"], book["date_borrowed"], book["borrowed_by"]))
    print(f"Sample books data inserted successfully, inserted {
          len(books)} books")

    cur.execute(sql.SQL("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))


def connection(dbname=None):
    try:
        cnx = connect(**{key: value for (key, value) in CONNECTION_CONFIG.items()
                      if key != "dbname"}, dbname=dbname if dbname else CONNECTION_CONFIG['dbname'])
    except Error as e:
        print(f"Error: {e}")
        print(f"Connecting to default database {DEFAULT_DB_NAME}...")
        try:
            cnx = connect(**{key: value for (key, value) in CONNECTION_CONFIG.items()
                          if key != "dbname"}, dbname=DEFAULT_DB_NAME)
        except Error as e:
            print(f"Error: {e}")
            return None
        else:
            print(f"Connection to {DEFAULT_DB_NAME} successful")
            print(f"Initializing database {DB_NAME}...")
            database_init(conn=cnx, cur=cnx.cursor())
            print(f"Database {DB_NAME} initialized successfully")
            cnx = connect(**{key: value for (key, value) in CONNECTION_CONFIG.items()
                             if key != "dbname"}, dbname=dbname if dbname else CONNECTION_CONFIG['dbname'])
    finally:
        return cnx


conn = connection()
cur = conn.cursor()


# Books operations -----------------------------------------


def get_books(branch_id: str | None = None, search_query: str | None = None) -> list[schemas.Book]:
    if branch_id and search_query:
        cur.execute(sql.SQL(
            "SELECT books.*, users.username as borrowed_by FROM books LEFT JOIN users ON books.borrowed_by = users.id WHERE books.branch = %s AND (books.title %% %s OR books.author %% %s);"), (branch_id, search_query, search_query))
    elif search_query:
        cur.execute(sql.SQL(
            "SELECT books.*, users.username as borrowed_by FROM books LEFT JOIN users ON books.borrowed_by = users.id WHERE books.title %% %s OR books.author %% %s;"), (search_query, search_query))
    elif branch_id:
        cur.execute(sql.SQL("SELECT books.*, users.username as borrowed_by FROM books LEFT JOIN users ON books.borrowed_by = users.id WHERE books.branch = %s;"),
                    (branch_id,))
    else:
        cur.execute(sql.SQL(
            "SELECT books.*, users.username as borrowed_by FROM books LEFT JOIN users ON books.borrowed_by = users.id;"))
    books = cur.fetchall()
    return books


def get_book(book_id: int) -> schemas.Book | None:
    cur.execute(sql.SQL("SELECT * FROM books WHERE id = %s;"),
                (str(book_id),))
    book = cur.fetchone()
    if not book:
        return None
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
                    (str(book_id),))
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


def return_book(book_id) -> bool:
    try:
        cur.execute(sql.SQL(
            "UPDATE books SET is_borrowed = FALSE, borrowed_by = NULL WHERE id = %s;"), (str(book_id),))
    except Error as e:
        print(f"Error returning book: {e}")
        return False
    else:
        print(f"Book id={book_id} returned successfully")
        return True


def get_user_books(user_id) -> list[schemas.Book]:
    cur.execute(sql.SQL("SELECT * FROM books WHERE borrowed_by = %s;"),
                (str(user_id),))
    books = cur.fetchall()
    return books

# Branches operations -----------------------------------------


def get_branches() -> list[schemas.Branch]:
    cur.execute(sql.SQL("SELECT * FROM branches;"))
    branches = cur.fetchall()
    return branches


def get_branch(branch_id: int) -> schemas.Branch:
    cur.execute(sql.SQL("SELECT * FROM branches WHERE id = %s;"),
                (str(branch_id),))
    branch = cur.fetchone()
    return branch


def add_branch(branch: schemas.BranchAdd) -> schemas.Branch:
    name = branch.name
    location = branch.location
    branch_added = ""

    try:
        cur.execute(sql.SQL("INSERT INTO branches (name, location) VALUES (%s, %s) RETURNING *;"),
                    (name, location))
        branch_added = cur.fetchone()
    except Error as e:
        print(f"Error adding branch: {e}")
        return False
    else:
        print(f"Branch added successfully: {branch_added}")
        return branch_added


def delete_branch(branch_id) -> bool:
    try:
        cur.execute(sql.SQL("DELETE FROM branches WHERE id = %s;"),
                    (str(branch_id),))
    except Error as e:
        print(f"Error deleting branch: {e}")
        return False
    else:
        print(f"Branch id={branch_id} deleted successfully")
        return True

# Users operations -----------------------------------------


def get_user(user_id: int) -> schemas.UserInDB:
    cur.execute(sql.SQL("SELECT * FROM users WHERE id = %s;"),
                (str(user_id),))
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


def add_user(user: schemas.UserAdd) -> schemas.UserInDB:
    username = user.username
    email = user.email
    name = user.name
    surname = user.surname
    password = user.password
    user_added = ""

    try:
        cur.execute(sql.SQL("""INSERT INTO users (username, email, name, surname, password) 
                            VALUES (%s, %s, %s, %s, %s) RETURNING *;"""),
                    [username, email, name, surname, password])
        user_added = cur.fetchone()
    except Error as e:
        print(f"Error adding user: {e}")
        return False
    else:
        print(f"User added successfully: {user_added}")
        return user_added
