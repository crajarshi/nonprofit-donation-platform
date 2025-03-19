import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.npo import NonProfitOrg
from app.models.user import User


def test_register_npo(
    client: TestClient, 
    db: Session, 
    normal_user_token_headers: dict
) -> None:
    """
    Test registering a new non-profit organization.
    """
    # Test data
    npo_data = {
        "name": "New Test NPO",
        "description": "A new test non-profit organization",
        "website": "https://newtestnpo.org",
        "xrpl_address": "rNewNPOXRPLAddress",
        "contact_email": "contact@newtestnpo.org",
        "contact_phone": "987-654-3210"
    }
    
    # Make the request
    response = client.post(
        f"{settings.API_V1_STR}/npos/register",
        json=npo_data,
        headers=normal_user_token_headers,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == npo_data["name"]
    assert data["description"] == npo_data["description"]
    assert data["website"] == npo_data["website"]
    assert data["xrpl_address"] == npo_data["xrpl_address"]
    assert data["contact_email"] == npo_data["contact_email"]
    assert data["contact_phone"] == npo_data["contact_phone"]
    assert "id" in data
    assert "is_verified" in data
    assert data["is_verified"] is False  # New NPOs should not be verified by default
    
    # Try to register another NPO (should fail as user already owns one)
    response = client.post(
        f"{settings.API_V1_STR}/npos/register",
        json={**npo_data, "name": "Another NPO"},
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400


def test_get_npo(
    client: TestClient, 
    db: Session, 
    npo: NonProfitOrg
) -> None:
    """
    Test getting a non-profit organization by ID.
    """
    # Make the request (no authentication required for viewing)
    response = client.get(
        f"{settings.API_V1_STR}/npos/{npo.id}",
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == npo.id
    assert data["name"] == npo.name
    assert data["description"] == npo.description
    assert data["website"] == npo.website
    assert data["xrpl_address"] == npo.xrpl_address
    assert data["contact_email"] == npo.contact_email
    
    # Try with non-existent NPO
    response = client.get(
        f"{settings.API_V1_STR}/npos/9999",  # Non-existent NPO ID
    )
    assert response.status_code == 404


def test_list_npos(
    client: TestClient, 
    db: Session, 
    npo: NonProfitOrg
) -> None:
    """
    Test listing non-profit organizations.
    """
    # Make the request
    response = client.get(
        f"{settings.API_V1_STR}/npos/",
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(n["id"] == npo.id for n in data)
    
    # Test including unverified NPOs
    response = client.get(
        f"{settings.API_V1_STR}/npos/?verified_only=false",
    )
    assert response.status_code == 200
    data = response.json()
    assert any(n["id"] == npo.id for n in data)


def test_update_npo(
    client: TestClient, 
    db: Session, 
    normal_user_token_headers: dict,
    npo: NonProfitOrg
) -> None:
    """
    Test updating a non-profit organization.
    """
    # Test data
    update_data = {
        "description": "Updated description",
        "website": "https://updated-npo.org",
        "contact_phone": "555-555-5555"
    }
    
    # Make the request
    response = client.put(
        f"{settings.API_V1_STR}/npos/{npo.id}",
        json=update_data,
        headers=normal_user_token_headers,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == npo.id
    assert data["description"] == update_data["description"]
    assert data["website"] == update_data["website"]
    assert data["contact_phone"] == update_data["contact_phone"]
    assert data["name"] == npo.name  # Should remain unchanged
    
    # Try to update verification status (should be ignored for non-admin users)
    response = client.put(
        f"{settings.API_V1_STR}/npos/{npo.id}",
        json={"is_verified": True},
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_verified"] is False  # Should remain unchanged
    
    # Try to update as a different user (should fail)
    # Create a new user first
    new_user_data = {
        "email": "anotheruser@example.com",
        "password": "anotherpass123",
        "full_name": "Another User",
        "xrpl_address": "rAnotherXRPLAddress"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json=new_user_data,
    )
    assert response.status_code == 200
    
    # Login as the new user
    login_data = {
        "username": new_user_data["email"],
        "password": new_user_data["password"],
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
    )
    assert response.status_code == 200
    other_user_token = response.json()["access_token"]
    other_user_headers = {"Authorization": f"Bearer {other_user_token}"}
    
    # Try to update the NPO as the new user
    response = client.put(
        f"{settings.API_V1_STR}/npos/{npo.id}",
        json={"description": "Unauthorized update"},
        headers=other_user_headers,
    )
    assert response.status_code == 403


def test_admin_verify_npo(
    client: TestClient, 
    db: Session, 
    admin_user_token_headers: dict,
    npo: NonProfitOrg
) -> None:
    """
    Test admin verifying a non-profit organization.
    """
    # Verify the NPO as admin
    response = client.put(
        f"{settings.API_V1_STR}/npos/{npo.id}",
        json={"is_verified": True},
        headers=admin_user_token_headers,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == npo.id
    assert data["is_verified"] is True
    
    # Unverify the NPO as admin
    response = client.put(
        f"{settings.API_V1_STR}/npos/{npo.id}",
        json={"is_verified": False},
        headers=admin_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_verified"] is False


def test_submit_proof(
    client: TestClient, 
    db: Session, 
    normal_user_token_headers: dict,
    npo: NonProfitOrg
) -> None:
    """
    Test submitting proof of fund utilization.
    """
    # Create a test file
    test_file = io.BytesIO(b"Test file content for proof submission")
    test_file.name = "test_proof.pdf"
    
    # Make the request
    response = client.post(
        f"{settings.API_V1_STR}/npos/{npo.id}/proof",
        data={"proof_description": "Test proof of fund utilization"},
        files={"proof_file": ("test_proof.pdf", test_file, "application/pdf")},
        headers=normal_user_token_headers,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == npo.id
    
    # Try as a different user (should fail)
    # Create a new user first
    new_user_data = {
        "email": "yetanotheruser@example.com",
        "password": "yetanotherpass123",
        "full_name": "Yet Another User",
        "xrpl_address": "rYetAnotherXRPLAddress"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json=new_user_data,
    )
    assert response.status_code == 200
    
    # Login as the new user
    login_data = {
        "username": new_user_data["email"],
        "password": new_user_data["password"],
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
    )
    assert response.status_code == 200
    other_user_token = response.json()["access_token"]
    other_user_headers = {"Authorization": f"Bearer {other_user_token}"}
    
    # Try to submit proof as the new user
    test_file = io.BytesIO(b"Unauthorized proof submission")
    test_file.name = "unauthorized_proof.pdf"
    
    response = client.post(
        f"{settings.API_V1_STR}/npos/{npo.id}/proof",
        data={"proof_description": "Unauthorized proof"},
        files={"proof_file": ("unauthorized_proof.pdf", test_file, "application/pdf")},
        headers=other_user_headers,
    )
    assert response.status_code == 403


def test_get_npo_campaigns(
    client: TestClient, 
    db: Session, 
    npo: NonProfitOrg,
    campaign: Campaign
) -> None:
    """
    Test getting campaigns for a specific non-profit organization.
    """
    # Make the request
    response = client.get(
        f"{settings.API_V1_STR}/npos/{npo.id}/campaigns",
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(c["id"] == campaign.id for c in data)
    
    # Test filtering by active status
    response = client.get(
        f"{settings.API_V1_STR}/npos/{npo.id}/campaigns?active_only=true",
    )
    assert response.status_code == 200
    data = response.json()
    assert all(c["is_active"] for c in data)
    
    # Try with non-existent NPO
    response = client.get(
        f"{settings.API_V1_STR}/npos/9999/campaigns",  # Non-existent NPO ID
    )
    assert response.status_code == 404 