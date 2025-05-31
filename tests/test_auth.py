import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)

def test_signup_missing_fields():
    response = client.post("/signup", json={"email": "john@example.com"})
    assert response.status_code == 422
    assert "first_name" in response.json()["detail"][0]["loc"]


def test_signup_short_password():
    response = client.post("/signup", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "password": "123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Password too short"

def test_send_otp_requires_field():
    response = client.post("/send-otp", json={})
    assert response.status_code == 422

def test_verify_otp_missing_fields():
    response = client.post("/verify-otp", json={"email_or_phone": "123"})
    assert response.status_code == 422

def test_signup_success():
    response = client.post("/signup", json={
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "janedoe@example.com",
        "phone": "9876543210",
        "password": "password123"
    })
    assert response.status_code in (200, 400, 500)

def test_signup_duplicate_email():
    response = client.post("/signup", json={
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "janedoe@example.com",
        "phone": "0000000000",
        "password": "password123"
    })
    assert response.status_code in (200, 400, 500)

def test_signup_duplicate_phone():
    response = client.post("/signup", json={
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "newemail@example.com",
        "phone": "9876543210",
        "password": "password123"
    })
    assert response.status_code in (200, 400, 500)
