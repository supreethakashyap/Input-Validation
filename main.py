import re
from flask import Flask, request, jsonify, abort
from sqlalchemy import create_engine, Column, Integer, String
import sqlite3
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt, verify_jwt_in_request
)
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change this in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # Token expires after one day

jwt = JWTManager(app)

# Database setup
engine = create_engine("sqlite:///phonebook.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)  

class PhoneBook(Base):
    __tablename__ = "phonebook"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, unique=True)
    phone_number = Column(String, unique=True)

Base.metadata.create_all(engine)

# Regular expressions for validation
name_pattern = re.compile(r"^[A-Z][a-zA-Z]*[-']?[a-zA-Z]+,? ?[a-zA-Z]*[-']?[a-zA-Z]+ ?[a-zA-Z]*[-']?[a-zA-Z]*[.]?$")
phone_number_pattern = re.compile(r"^\d{5}$|^\d{5}[. ]\d{5}$|^\d{3}[-. ]\d{4}$|^\+?\b([1-9]|[1-9][0-9]|[1-9][0-9][0-8])\b[-.\( ]{0,2}\d{2,3}[ \-.\)]{0,2}\d{3}[-. ]\d{4}$|^[-.\( ]?\d{2,3}[ \-.\)]\d{3}[-. ]\d{4}$|^(00|011)[-.\( ]?\d{0,3}[ -.\)][-.\( ]?\d{2,3}[ -.\)]\d{3}[-. ]\d{4}$|^[+45. ]{0,4}\d{4}[. ]\d{4}$|^[+45. ]{0,4}\d{2}[. ]\d{2}[. ]\d{2}[. ]\d{2}$")

def validate_name(name):
    return bool(name_pattern.match(name))

def validate_phone_number(phone_number):
    return bool(phone_number_pattern.match(phone_number))

# Set up audit logging
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)
fh = RotatingFileHandler('audit.log', maxBytes=10000, backupCount=1)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
audit_logger.addHandler(fh)

# Authentication and roles setup
def authenticate(username, password):
    users = {
        "user": {"password": "password", "role": "read"},
        "admin": {"password": "adminpassword", "role": "read/write"}      
    }
    user = users.get(username)
    if user and user['password'] == password:
        return user
    return None
@app.route("/")
def home():
    return "Welcome to PhoneBook Project! Open Postman for further and refer to the collections folder"

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = authenticate(username, password)
    if user:
        # Create a token with the user information directly accessible in the token
        access_token = create_access_token(identity={'username': username, 'role': user['role']})
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

def jwt_required_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_claims = claims['sub']  # Use 'sub' instead of 'identity'
            if user_claims['role'] not in roles:
                abort(403, description="Forbidden: Insufficient rights")
            return fn(*args, **kwargs)
        return wrapper
    return decorator



# API Endpoints
@app.route("/PhoneBook/list", methods=["GET"])
@jwt_required_role('read', 'read/write')
def list_phonebook():
    session = Session()
    try:
        phonebook_entries = session.query(PhoneBook).all()
        results = [{"full_name": entry.full_name, "phone_number": entry.phone_number} for entry in phonebook_entries]
        return jsonify(results)
    except Exception as e:
        session.rollback()
        audit_logger.error(f"Failed to fetch phonebook entries: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/PhoneBook/add", methods=["POST"])
@jwt_required_role('read/write')
def add_person():
    session = Session()
    try:
        data = request.json
        full_name = data.get("full_name", "")
        phone_number = data.get("phone_number", "")
        if not validate_name(full_name) or not validate_phone_number(phone_number):
            return jsonify({"message": "Invalid name or phone number format"}), 400

        new_person = PhoneBook(full_name=full_name, phone_number=phone_number)
        session.add(new_person)
        session.commit()
        audit_logger.info(f'Person added: {full_name}')
        return jsonify({"message": "Person added successfully"}), 200
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Person already exists in the database"}), 400
    except Exception as e:
        session.rollback()
        audit_logger.error(f'Failed to add person: {str(e)}')
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/PhoneBook/deleteByName", methods=["PUT"])
@jwt_required_role('read/write')
def delete_person():
    full_name = request.args.get("full_name")
    session = Session()
    try:
        # person = session.query(PhoneBook).filter_by(full_name=full_name).first()
        persons = session.query(PhoneBook).all()
        person = next((p for p in persons if p.full_name == full_name), None)

        if not person:
            audit_logger.info(f'Person not found for deletion: {full_name}')
            return jsonify({"message": "Person not found in the database"}), 404
        session.delete(person)
        session.commit()
        audit_logger.info(f'Person deleted: {full_name}')
        return jsonify({"message": "Person deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        audit_logger.error(f'Error deleting person: {str(e)}')
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/PhoneBook/deleteByPhone", methods=["PUT"])
@jwt_required_role('read/write')
def delete_person_by_phone():
    phone_number = request.args.get("phone_number")
    session = Session()
    try:
        person = session.query(PhoneBook).filter_by(phone_number=phone_number).first()
        if not person:
            audit_logger.info(f'Person not found for deletion with phone number: {phone_number}')
            return jsonify({"message": "Number not found in the database"}), 404

        session.delete(person)
        session.commit()
        audit_logger.info(f'Person deleted with phone number: {phone_number}')
        return jsonify({"message": "Person deleted successfully"}), 200

    except Exception as e:
        session.rollback()
        audit_logger.error(f'Error deleting person by phone number: {str(e)}')
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)
