import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.donation import Donation
from app.models.campaign import Campaign
from app.models.npo import NonProfitOrg
from app.models.user import User


def test_create_donation(
    client: TestClient, 
    db: Session, 
    normal_user_token_headers: dict,
    normal_user: User,
    campaign: Campaign
) -> None:
    """
    Test creating a new donation.
    """
    # Test data
    donation_data = {
        "amount": 100.0,
        "currency": "XRP",
        "campaign_id": campaign.id,
        "npo_id": campaign.npo_id,
        "message": "Test donation from automated test",
        "is_anonymous": False,
        "use_escrow": False
    }
    
    # Make the request
    response = client.post(
        f"{settings.API_V1_STR}/donations/initiate",
        json=donation_data,
        headers=normal_user_token_headers,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == donation_data["amount"]
    assert data["currency"] == donation_data["currency"]
    assert data["campaign_id"] == donation_data["campaign_id"]
    assert data["npo_id"] == donation_data["npo_id"]
    assert data["message"] == donation_data["message"]
    assert data["is_anonymous"] == donation_data["is_anonymous"]
    
    # Try with invalid campaign
    donation_data["campaign_id"] = 9999  # Non-existent campaign
    response = client.post(
        f"{settings.API_V1_STR}/donations/initiate",
        json=donation_data,
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404


def test_get_donation(
    client: TestClient, 
    db: Session, 
    normal_user_token_headers: dict,
    donation: Donation
) -> None:
    """
    Test getting a donation by ID.
    """
    # Make the request
    response = client.get(
        f"{settings.API_V1_STR}/donations/{donation.id}",
        headers=normal_user_token_headers,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == donation.id
    assert data["amount"] == donation.amount
    assert data["currency"] == donation.currency
    assert data["status"] == donation.status
    
    # Try with non-existent donation
    response = client.get(
        f"{settings.API_V1_STR}/donations/9999",  # Non-existent donation ID
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404


def test_list_donations(
    client: TestClient, 
    db: Session, 
    normal_user_token_headers: dict,
    donation: Donation
) -> None:
    """
    Test listing donations.
    """
    # Make the request
    response = client.get(
        f"{settings.API_V1_STR}/donations/",
        headers=normal_user_token_headers,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Should at least have the donation from the fixture
    assert any(d["id"] == donation.id for d in data)
    
    # Test filtering by campaign
    response = client.get(
        f"{settings.API_V1_STR}/donations/?campaign_id={donation.campaign_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert all(d["campaign_id"] == donation.campaign_id for d in data)
    
    # Test filtering by NPO
    response = client.get(
        f"{settings.API_V1_STR}/donations/?npo_id={donation.npo_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert all(d["npo_id"] == donation.npo_id for d in data)


def test_admin_list_all_donations(
    client: TestClient, 
    db: Session, 
    admin_user_token_headers: dict,
    donation: Donation
) -> None:
    """
    Test admin can list all donations regardless of ownership.
    """
    # Make the request as admin
    response = client.get(
        f"{settings.API_V1_STR}/donations/",
        headers=admin_user_token_headers,
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(d["id"] == donation.id for d in data)
    
    # Create a different user's donation
    new_user_data = {
        "email": "otheruser@example.com",
        "password": "otheruserpass123",
        "full_name": "Other User",
        "xrpl_address": "rOtherXRPLAddress"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json=new_user_data,
    )
    assert response.status_code == 200
    
    # Login as other user
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
    
    # Create donation as other user
    donation_data = {
        "amount": 200.0,
        "currency": "XRP",
        "campaign_id": donation.campaign_id,
        "npo_id": donation.npo_id,
        "message": "Other user donation",
        "is_anonymous": False,
        "use_escrow": False
    }
    response = client.post(
        f"{settings.API_V1_STR}/donations/initiate",
        json=donation_data,
        headers=other_user_headers,
    )
    assert response.status_code == 200
    other_donation_id = response.json()["id"]
    
    # Admin should see both donations
    response = client.get(
        f"{settings.API_V1_STR}/donations/",
        headers=admin_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert any(d["id"] == donation.id for d in data)
    assert any(d["id"] == other_donation_id for d in data)
    
    # Normal user should only see their own donations
    response = client.get(
        f"{settings.API_V1_STR}/donations/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert any(d["id"] == donation.id for d in data)
    assert not any(d["id"] == other_donation_id for d in data) 