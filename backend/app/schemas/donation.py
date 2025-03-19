from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class DonationBase(BaseModel):
    """Base donation schema."""
    amount: Decimal = Field(..., gt=0)
    campaign_id: Optional[int] = None
    npo_id: int
    message: Optional[str] = Field(None, max_length=500)
    is_anonymous: bool = False
    xrpl_transaction_hash: Optional[str] = None


class DonationCreate(DonationBase):
    """Schema for creating a donation."""
    pass


class DonationUpdate(BaseModel):
    """Schema for updating a donation."""
    xrpl_transaction_hash: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|completed|failed)$")


class Donation(DonationBase):
    """Complete donation schema."""
    id: int
    donor_id: int
    status: str = Field(..., pattern="^(pending|completed|failed)$")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 