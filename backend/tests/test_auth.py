"""
Unit tests for authentication endpoints.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database.session import Base, get_db

# Use a dedicated test database file (removed and recreated each session)
SQLALCHEMY_TEST_URL = "sqlite:///./test_auth.db"

# Remove old test DB to ensure a clean slate on every test run
if os.path.exists("test_auth.db"):
    os.remove("test_auth.db")

engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_register_success():
    resp = client.post("/auth/register", json={
        "email": "test@voyage.ai",
        "username": "testuser",
        "password": "SecurePass123",
        "full_name": "Test User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["username"] == "testuser"


def test_register_duplicate_email():
    client.post("/auth/register", json={
        "email": "dup@voyage.ai",
        "username": "dupuser",
        "password": "pass123",
    })
    resp = client.post("/auth/register", json={
        "email": "dup@voyage.ai",
        "username": "dupuser2",
        "password": "pass123",
    })
    assert resp.status_code == 400


def test_login_success():
    client.post("/auth/register", json={
        "email": "login@voyage.ai",
        "username": "loginuser",
        "password": "Pass@word1",
    })
    resp = client.post("/auth/login", json={
        "email": "login@voyage.ai",
        "password": "Pass@word1",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password():
    client.post("/auth/register", json={
        "email": "wrong@voyage.ai",
        "username": "wronguser",
        "password": "correct_pass",
    })
    resp = client.post("/auth/login", json={
        "email": "wrong@voyage.ai",
        "password": "wrong_pass",
    })
    assert resp.status_code == 401


def test_profile_requires_auth():
    resp = client.get("/user/profile")
    assert resp.status_code == 403
