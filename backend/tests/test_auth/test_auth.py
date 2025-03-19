import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings


def test_signup(client: TestClient, db: Session) -> None:
    """
    Test user registration.
    """
    # Test data
    user_data = {
        "email": "newuser@example.com",
        "password": "newuserpass123",
        "full_name": "New User",
        "xrpl_address": "rNewUserXRPLAddress"
    }
    
    # Make the request
    response = client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json=user_data,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["xrpl_address"] == user_data["xrpl_address"]
    assert "id" in data
    assert "hashed_password" not in data
    
    # Try to create the same user again (should fail)
    response = client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json=user_data,
    )
    assert response.status_code == 400


def test_login(client: TestClient, normal_user: dict) -> None:
    """
    Test user login.
    """
    # Login data
    login_data = {
        "username": "user@example.com",  # Use the normal_user fixture email
        "password": "password123",
    }
    
    # Make the request
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Try with incorrect password
    login_data["password"] = "wrongpassword"
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
    )
    assert response.status_code == 401
    
    # Try with non-existent user
    login_data["username"] = "nonexistent@example.com"
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
    )
    assert response.status_code == 401


def test_get_me(client: TestClient, normal_user_token_headers: dict) -> None:
    """
    Test getting the current user profile.
    """
    # Make the request with token headers
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers=normal_user_token_headers,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data
    
    # Try without token (should fail)
    response = client.get(f"{settings.API_V1_STR}/auth/me")
    assert response.status_code == 401 