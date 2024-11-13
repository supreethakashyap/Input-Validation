# Input-Validation
This project involves implementing a phonebook application using Python Flask, Docker, and SQLite. The application provides endpoints for adding, listing, and deleting phonebook entries, with JWT-based authentication. The project also provides audit log functionality. 
## Technologies Used
- **Python**: Multipurpose programming language with a rich library collection.
- **Flask**: A Python microframework used to build APIs.
- **SQLite**: SQL database for storing name and phone number values.
- **SQLAlchemy**: A popular SQL toolkit and Object Relational Mapper (ORM) for Python.
- **Docker**: Used to containerize the application for easy deployment.
- **Postman**: Used to test API endpoints and help with API development.

## Project Setup

### Docker Build and Run
1. **Build the Docker Image**  
   Navigate to the project directory containing the Dockerfile and build the Docker image:
   ```sh
   docker build -t phonebook-app .
   ```
2. **Run the Application**  
   Start the application on port 5000:
   ```sh
   docker run -p 5000:5000 phonebook-app
   ```

### Running Flask Application Locally
1. **Set Flask App**  
   Set the Flask app to `main.py`:
   ```sh
   set FLASK_APP=main.py
   ```
2. **Install Requirements**  
   Install all required packages from `requirements.txt`:
   ```sh
   pip install -r requirements.txt
   ```
3. **Run Flask Application**  
   Run the application:
   ```sh
   python -m flask run
   ```

## API Endpoints
- **Authentication**
  - `/login (POST)` - Generate JWT token
- **Phonebook Operations**
  - `/PhoneBook/list (GET)` - View the list of names and phone numbers
  - `/PhoneBook/add (POST)` - Add details to the database
  - `/PhoneBook/deleteByPhone (PUT)` - Delete details by phone number
  - `/PhoneBook/deleteByName (PUT)` - Delete details by name

## Database
The project uses an **SQLite 3** database to store the name and phone number values.

## Authentication
**JWT Token** is used for securing API endpoints. Obtain a JWT token using the `/PhoneBook/login` (POST) method. The token is valid for **24 hours**.

## Testing
- **Test Cases**: There are 9 test cases written for the program, which can be found in `test_cases.py`.
- **Prerequisites**: The `conftest.py` file is used to obtain tokens required by `test_cases.py`.
- **Run Test Cases**:
  1. Install the pytest module:
     ```sh
     pip install pytest
     ```
  2. Run the test cases:
     ```sh
     python -m pytest
     ```
