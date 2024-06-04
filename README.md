# Library System
A small API project done with FastAPI for methods and techniques of programming course at AGH UST.  

## Libraries used:
- fastapi
- pydantic
- uvicorn
- psycopg
- python-dotenv
- pyjwt
- passlib[bcrypt]

## How to run
1. Clone the repository
2. Install docker and docker-compose, if you have them already skip this step
3. Run `docker-compose up --build` in the root directory of the project
4. API should be available at `http://localhost:80`


## API structure

[Link to documentation](http://0.0.0.0/docs)
### Auth
- POST `/login/` - takes UserLogin class object and returns JWT token
- POST `/register/` - takes UserRegister class object and adds that user to database and returns JWT token
  
### Books
- GET `/books/` - gets all books from database
- GET `/books/me/` - gets all books borrowed by user whose JWT token was used
- GET `/book/{book_id}/` - gets a book with that `book_id` from database
- POST `/book/` - takes BookAdd class object and adds that book to database, only for logged in users with admin privilages
- DELETE `/book/{book_id}/` - deletes book object with `book_id` from database, only for logged in users with admin privilages
- PUT `/book/{book_id}/borrow/` - sets book with `book_id` as borrowed by user whose JWT token was used
- PUT `/book/{book_id}/return/` - sets book with `book_id` as returned by user whose JWT token was used

