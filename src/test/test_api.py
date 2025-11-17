import pytest
import asyncio

from pwdlib import PasswordHash

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

from user_service_v2.models.user import (
    Base,
    UserRepositoryV2,
    User,
    get_user_repository_v2
)

from mindfuly.api import app

"""
FIXTURES AND HELPERS
"""

@pytest.fixture(scope='function')
def engine():
    engine = create_engine("sqlite:///:memory:?check_same_thread=False")
    Base.metadata.create_all(bind=engine)
    yield engine

@pytest.fixture(scope='function')
def session(engine):
    conn = engine.connect()
    conn.begin()
    db = Session(bind=conn)
    yield db
    db.rollback()
    conn.close()

@pytest.fixture(scope='function')
def repo_v2(session):
    yield UserRepositoryV2(session)

@pytest.fixture(scope='function')
def client(repo_v2):
    app.dependency_overrides[get_user_repository_v2] = lambda: repo_v2
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope='function')
def created_user(session):
    # Store a proper hashed password so repository verify_password (pwdlib) can identify it
    hashed = PasswordHash.recommended().hash("bass")
    user_data = {"name": "foo", "id": 5,  "email": "fee", "hashed_password": hashed, "tier": 1}
    session.execute(text("INSERT INTO users (name, id, email, hashed_password, tier) VALUES (:name, :id, :email, :hashed_password, :tier)"), user_data)
    session.commit()
    return user_data

def test_delete_user(client, created_user):
    response = client.delete(f"/users/{created_user['id']}")
    assert response.status_code == 204

    get_response = client.get(f"/users/{created_user['name']}")
    assert get_response.json() == {"user": None}

def test_delete_nonexistent_user(client):
    response = client.delete("/users/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

"""
API TESTS
"""

# Ensure that we can create a user via the POST endpoint
def test_create_user(client, repo_v2):
    response = client.post(
        "/users/create_user",
        # id is ignored so we can put any value here
        json={"id": 69, "name": "name1", "email": "email2", "hashed_password": "pass3"},
    )

    assert response.status_code == 201 # Response should be 201
    new_user: User
    new_user = asyncio.run(repo_v2.get_by_name("name1"))
    assert repo_v2.password_hash.verify("pass3", new_user.hashed_password) # Verify should return true
    assert new_user.name == "name1" # Name should match
    assert new_user.email == "email2" # Email should match

# Ensure that we can read a user via the GET endpoint
def test_read_user(client, created_user):
    response = client.get(f"/users/{created_user['name']}")
    assert response.status_code == 200 # Response should be 200
    assert response.json() == created_user

# Ensure that we can list users via the GET endpoint
def test_list_users(client, created_user):
    response = client.get("/users/")
    assert response.status_code == 200 # Response should be 200
    assert response.json() == {
        "users": [created_user] # The list of users should contain the created user
    }

# Ensure that we cannot create an existing user via the POST endpoint
def test_create_existing_user(client, created_user):
    response = client.post(
        "/users/create_user",
        json=created_user,
    )
    assert response.status_code == 409 # Response should be 409
    assert response.json() == {"detail": "User already exists"} # Error detail should match

# Ensure that we can delete a user via the DELETE endpoint
def test_delete_user(client, created_user):
    response = client.request(
        "DELETE",
        f"/users/{created_user['name']}"
    )
    assert response.status_code == 204 # Response should be 204

    get_response = client.get(f"/users/{created_user['name']}")
    assert get_response.json() == {"detail": "User not found"} # User should no longer exist

# Ensure that we cannot delete a nonexistent user via the DELETE endpoint
def test_delete_nonexistent_user(client):
    response = client.request(
        "DELETE",
        "/users/fakey"
    )
    assert response.status_code == 404 # Response should be 404
    assert response.json() == {"detail": "User not found"} # Error detail should match