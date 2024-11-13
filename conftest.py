import pytest
from flask_jwt_extended import create_access_token
from main import app, Base, engine  # Ensure correct import from your application structure

@pytest.fixture(scope="module")
def test_app():
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'super-secret-key-test'  # Use a different secret key for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./test_phonebook.db"
    
    # Setup the database
    Base.metadata.create_all(engine)

    yield app 

    # Teardown the database
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="module")
def client(test_app):
    return test_app.test_client()

@pytest.fixture(scope="module")
def tokens(test_app):
    with test_app.app_context():
        access_token = create_access_token(identity={'username': 'admin', 'role': 'read/write'})
    return {
        "access": access_token
    }
