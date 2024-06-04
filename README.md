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
3. Create `.env` file in the root directory of the project with the following content:
```yml
# Connection parameters for the database
DB_HOST=db
DB_PORT=5432
DB_NAME=library_system
DB_USER=postgres
DB_PASSWORD=secret

# Auth security parameters
JWT_SECRET=c0f9236446682cbebc5ec8683881259cddf8c52dd987fa5c4f05a144ea7fd3ea
JWT_EXPIRATION=3600
JWT_ALGORITHM=HS256
```
3. Run the command below in the root directory of the project
```shell
docker-compose up --build
``` 
4. API should be available at [http://localhost:80](http://localhost:80)


## API structure

[Link to documentation](http://0.0.0.0/docs)


### Auth
- POST `/login/` - takes UserLogin class object and returns JWT token
- POST `/register/` - takes UserRegister class object and adds that user to database and returns JWT token
- GET `/current_user/` - returns User class object of user whose JWT token was used

Sample user for testing:
```json
{
    "username": "user",
    "password": "password"
}
```
  
### Books
- GET `/books/` - gets all books from database
- GET `/books/me/` - gets all books borrowed by user whose JWT token was used
- GET `/book/{book_id}/` - gets a book with that `book_id` from database
- POST `/book/` - takes BookAdd class object and adds that book to database, only for logged in users with admin privilages
- DELETE `/book/{book_id}/` - deletes book object with `book_id` from database, only for logged in users with admin privilages
- PUT `/book/{book_id}/borrow/` - sets book with `book_id` as borrowed by user whose JWT token was used
- PUT `/book/{book_id}/return/` - sets book with `book_id` as returned by user whose JWT token was used

### Branches
- GET `/branches/` - gets all branches from database
- GET `/branch/{branch_id}/` - gets a branch with that `branch_id` from database
- POST `/branch/` - takes BranchAdd class object and adds that branch to database, only for logged in users with admin privilages
- DELETE `/branch/{branch_id}/` - deletes branch object with `branch_id` from database, only for logged in users with admin privilages
