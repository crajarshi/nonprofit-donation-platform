from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from decimal import Decimal

class CampaignBase(BaseModel):
    """Base campaign schema."""
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=2000)
    goal_amount: Decimal = Field(..., gt=0)
    start_date: datetime
    end_date: Optional[datetime] = None
    cover_image: Optional[HttpUrl] = None
    media_urls: Optional[List[HttpUrl]] = None
    offers_nft: bool = False
    nft_details: Optional[dict] = None
    governance_token: bool = False
    token_details: Optional[dict] = None


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign."""
    npo_id: int


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    goal_amount: Optional[Decimal] = Field(None, gt=0)
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    cover_image: Optional[HttpUrl] = None
    media_urls: Optional[List[HttpUrl]] = None
    nft_details: Optional[dict] = None
    token_details: Optional[dict] = None


class Campaign(CampaignBase):
    """Complete campaign schema."""
    id: int
    npo_id: int
    current_amount: Decimal = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_donors: int = 0
    total_donations: int = 0

    class Config:
        from_attributes = True 