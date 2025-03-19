import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    ALGORITHM,
)
from app.core.config import settings


def test_password_hashing():
    """
    Test password hashing and verification.
    """
    password = "test-password"
    hashed_password = get_password_hash(password)
    
    # Verify hashed password is different from original
    assert hashed_password != password
    
    # Verify correct password
    assert verify_password(password, hashed_password)
    
    # Verify incorrect password
    assert not verify_password("wrong-password", hashed_password)


def test_create_access_token():
    """
    Test JWT token creation and validation.
    """
    # Create token with default expiry
    user_id = 123
    token = create_access_token(subject=user_id)
    
    # Decode and verify token
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert str(user_id) == payload["sub"]
    assert "exp" in payload
    
    # Test with custom expiry
    custom_expiry = timedelta(minutes=30)
    token = create_access_token(subject=user_id, expires_delta=custom_expiry)
    
    # Decode and verify token
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert str(user_id) == payload["sub"]
    assert "exp" in payload
    
    # Try with wrong secret key (should fail)
    with pytest.raises(jwt.JWTError):
        jwt.decode(token, "wrong-secret-key", algorithms=[ALGORITHM]) 