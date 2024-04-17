import json
from psycopg import connect, Error, sql
from dotenv import dotenv_values

CONNECTION_CONFIG = {
    'dbname': dotenv_values('.env')['DB_NAME'],
    'user': dotenv_values('.env')['DB_USER'],
    'password': dotenv_values('.env')['DB_PASSWORD'],
    'port': dotenv_values('.env')['DB_PORT'],
    'host': dotenv_values('.env')['DB_HOST'],
    'autocommit': True,
}

DB_NAME = "library_system"

def connection(dbname=None):
    try:
        cnx = connect(**{key:value for (key, value) in CONNECTION_CONFIG.items() if key != "dbname"}, dbname=dbname if dbname else CONNECTION_CONFIG['dbname'])
    except Error as e:
        print(f"Error: {e}")
        exit(1)
    else:
        return cnx
    
conn = connection()
cur = conn.cursor()

def database_init():
    # check if database already exists
    global cur, conn
    cur.execute("SELECT datname FROM pg_database")
    db_list = cur.fetchall()
    db_list = [db[0] for db in db_list]

    if DB_NAME in db_list:
        print("Error: Database already exists")

        # for development purposes, I will drop the database if it exists
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE);").format(sql.Identifier(DB_NAME)))
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
                        name VARCHAR(100), 
                        email VARCHAR(100), 
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
    print(f"Sample books data inserted successfully, inserted {len(books)} books")

    # populate the table with sample branches data from branches.json
    print(f"Populating table {DB_NAME}.branches with sample data...")
    with open("/workspaces/library_system/app/sample_data/branches.json", "r") as f:
        branches = json.load(f)
        for branch in branches:
            cur.execute(sql.SQL("""INSERT INTO branches (name, location) 
                                VALUES (%s, %s);"""),
                                (branch["name"], branch["location"]))
    print(f"Sample branch data inserted successfully, inserted {len(branches)} branches")

    # populate the table with sample users data from users.json
    print(f"Populating table {DB_NAME}.users with sample data...")
    with open("/workspaces/library_system/app/sample_data/users.json", "r") as f:
        users = json.load(f)
        for user in users:
            cur.execute(sql.SQL("""INSERT INTO users (name, email, password) 
                                VALUES (%s, %s, %s);"""),
                                (user["name"], user["email"], user["password"]))
    print(f"Sample user data inserted successfully, inserted {len(users)} users")

def get_books() -> list[dict]:
    cur.execute(sql.SQL("SELECT * FROM books;"))
    books = cur.fetchall()
    return books

def get_book(book_id) -> dict:
    cur.execute(sql.SQL("SELECT * FROM books WHERE id = %s;"), sql.Identifier(book_id))
    book = cur.fetchone()
    return book

def add_book(title, author, year, isbn, branch) -> dict:
    book_added = "siema"

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
        cur.execute(sql.SQL("DELETE FROM books WHERE id = %s;"), sql.Identifier(book_id))
    except Error as e:
        print(f"Error deleting book: {e}")
        return False
    else:
        print(f"Book id={book_id} deleted successfully")
        return True

# database_init()
add_book("The Alchenist", "Pauloo Coelho", 1989, "978-0062315807", "Fittion")
conn.close()