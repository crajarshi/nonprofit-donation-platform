from typing import Optional, Union, Any
from pydantic import BaseModel


class Token(BaseModel):
    """Schema for access token."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: Optional[int] = None  # subject (user id)
    exp: Optional[int] = None  # expiration time


class TokenCreate(BaseModel):
    """
    Token creation schema for digital assets (NFTs, governance tokens).
    """
    token_type: str
    token_id: str
    token_uri: Optional[str] = None
    token_amount: float = 1.0
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    donation_id: Optional[int] = None
    owner_id: int
    npo_id: int
    governance_power: float = 0.0 