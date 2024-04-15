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
                        id SERIAL PRIMARY KEY, 
                        title VARCHAR(100), 
                        author VARCHAR(100), 
                        year INTEGER, 
                        isbn VARCHAR(17),
                        branch VARCHAR(100),
                        is_borrowed BOOLEAN DEFAULT FALSE,
                        date_borrowed DATE,
                        borrowed_by VARCHAR(100)
                        );"""))
    print(f"Table {DB_NAME}.books created successfully")

    # populate the table with sample books data from books.json
    print(f"Populating table {DB_NAME}.books with sample data...")

    with open("/workspaces/library_system/app/books.json", "r") as f:
        books = json.load(f)
        for book in books:
            cur.execute(sql.SQL("""INSERT INTO books (title, author, year, isbn, branch, is_borrowed, date_borrowed, borrowed_by) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""),
                                (book["title"], book["author"], book["year"], book["isbn"], book["branch"], book["is_borrowed"], book["date_borrowed"], book["borrowed_by"]))
    print(f"Sample data inserted successfully, inserted {len(books)} books")

database_init()
conn.close()