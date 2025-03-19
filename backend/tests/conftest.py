import os
import pytest
from typing import Dict, Generator, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.models.npo import NonProfitOrg
from app.models.campaign import Campaign
from app.models.donation import Donation
from app.core import security
from app.services import user_service


# Create a test database URL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create test session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(bind=engine)  # Create the tables
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Drop the tables


@pytest.fixture(scope="function")
def client(db: TestSessionLocal) -> Generator:
    """
    Create a new FastAPI TestClient that uses the `db` fixture.
    """
    def _get_test_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def normal_user(db: TestSessionLocal) -> User:
    """
    Create a normal user for testing.
    """
    user_in = {
        "email": "user@example.com",
        "password": "password123",
        "full_name": "Test User",
        "xrpl_address": "rUserXRPLAddressExample"
    }
    user = user_service.create_user(db, user_in=user_in)
    return user


@pytest.fixture(scope="function")
def admin_user(db: TestSessionLocal) -> User:
    """
    Create an admin user for testing.
    """
    user_in = {
        "email": "admin@example.com",
        "password": "adminpass123",
        "full_name": "Admin User",
        "is_admin": True,
        "xrpl_address": "rAdminXRPLAddressExample"
    }
    user = user_service.create_user(db, user_in=user_in)
    return user


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, normal_user: User) -> Dict[str, str]:
    """
    Create token headers for the normal user.
    """
    return _get_token_headers(client, normal_user.email, "password123")


@pytest.fixture(scope="function")
def admin_user_token_headers(client: TestClient, admin_user: User) -> Dict[str, str]:
    """
    Create token headers for the admin user.
    """
    return _get_token_headers(client, admin_user.email, "adminpass123")


def _get_token_headers(client: TestClient, email: str, password: str) -> Dict[str, str]:
    """
    Helper function to get authentication token headers.
    """
    login_data = {
        "username": email,
        "password": password,
    }
    r = client.post("/api/v1/auth/login", data=login_data)
    tokens = r.json()
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def npo(db: TestSessionLocal, normal_user: User) -> NonProfitOrg:
    """
    Create a non-profit organization for testing.
    """
    from app.services import npo_service
    npo_in = {
        "name": "Test NPO",
        "description": "A test non-profit organization",
        "website": "https://testnpo.org",
        "xrpl_address": "rNPOXRPLAddressExample",
        "contact_email": "contact@testnpo.org",
        "contact_phone": "123-456-7890"
    }
    npo = npo_service.create_npo(db, obj_in=npo_in, owner_id=normal_user.id)
    return npo


@pytest.fixture(scope="function")
def campaign(db: TestSessionLocal, npo: NonProfitOrg) -> Campaign:
    """
    Create a campaign for testing.
    """
    from app.services import campaign_service
    from datetime import datetime, timedelta
    
    campaign_in = {
        "title": "Test Campaign",
        "description": "A test fundraising campaign",
        "goal_amount": 1000.0,
        "start_date": datetime.utcnow(),
        "end_date": datetime.utcnow() + timedelta(days=30),
        "is_active": True,
        "npo_id": npo.id
    }
    campaign = campaign_service.create_campaign(db, obj_in=campaign_in)
    return campaign


@pytest.fixture(scope="function")
def donation(db: TestSessionLocal, normal_user: User, campaign: Campaign) -> Donation:
    """
    Create a donation for testing.
    """
    from app.services import donation_service
    
    donation_in = {
        "amount": 50.0,
        "currency": "XRP",
        "campaign_id": campaign.id,
        "npo_id": campaign.npo_id,
        "message": "Test donation",
        "is_anonymous": False
    }
    donation = donation_service.create_donation(
        db, obj_in=donation_in, donor_id=normal_user.id
    )
    return donation 