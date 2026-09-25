import os
import pytest
from app import app, init_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_status_endpoint(client):
    response = client.get("/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"

def test_get_existing_user(client):
    response = client.get("/user?username=john_doe")
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "john_doe"

def test_user_not_found(client):
    response = client.get("/user?username=nonexistent_user_99")
    assert response.status_code == 404
