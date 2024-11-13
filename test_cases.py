import json

def test_generate_token(client, tokens):
    """Test token generation."""
    assert tokens["access"] is not None, "JWT token should be generated"

def test_use_token_to_access_protected(client, tokens):
    """Test accessing protected endpoint with token."""
    response = client.get("/PhoneBook/list", headers={'Authorization': f'Bearer {tokens["access"]}'})
    assert response.status_code == 200, "Should access with valid token"

def test_add_person(client, tokens):
    """Test adding a new person to the phonebook."""
    response = client.post("/PhoneBook/add", json={
        "full_name": "John Doe",
        "phone_number": "12345"
    }, headers={'Authorization': f'Bearer {tokens["access"]}'})
    assert response.status_code == 200, "Person should be added"

def test_add_person_invalid_phone(client, tokens):
    """Test adding a person with an invalid phone number."""
    response = client.post("/PhoneBook/add", json={
        "full_name": "Jane Doe",
        "phone_number": "abcde"  # Invalid phone number
    }, headers={'Authorization': f'Bearer {tokens["access"]}'})
    assert response.status_code == 400, "Should reject invalid phone number"

def test_add_person_invalid_name(client, tokens):
    """Test adding a person with an invalid name format."""
    response = client.post("/PhoneBook/add", json={
        "full_name": "1234",  # Invalid name
        "phone_number": "12345"
    }, headers={'Authorization': f'Bearer {tokens["access"]}'})
    assert response.status_code == 400, "Should reject invalid name format"

def test_add_duplicate_person(client, tokens):
    """Test adding a duplicate person to the phonebook."""
    client.post("/PhoneBook/add", json={
        "full_name": "Alice Smith",
        "phone_number": "54321"
    }, headers={'Authorization': f'Bearer {tokens["access"]}'})
    response = client.post("/PhoneBook/add", json={
        "full_name": "Alice Smith",
        "phone_number": "54321"
    }, headers={'Authorization': f'Bearer {tokens["access"]}'})
    assert response.status_code == 400, "Should reject duplicate entries"

def test_list_phonebook(client, tokens):
    """Test listing phonebook entries."""
    response = client.get("/PhoneBook/list", headers={'Authorization': f'Bearer {tokens["access"]}'})
    data = response.get_json()
    assert response.status_code == 200, "Should list entries"
    assert isinstance(data, list), "Response should be a list"

def test_delete_person_by_name(client, tokens):
    """Test deleting a person by name."""
    response = client.put("/PhoneBook/deleteByName?full_name=John Doe", headers={'Authorization': f'Bearer {tokens["access"]}'})
    assert response.status_code == 200, "Should delete by name"

def test_delete_person_by_phone(client, tokens):
    """Test deleting a person by phone number."""
    response = client.put("/PhoneBook/deleteByPhone?phone_number=54321", headers={'Authorization': f'Bearer {tokens["access"]}'})
    assert response.status_code == 200, "Should delete by phone number"
