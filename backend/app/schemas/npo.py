from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, HttpUrl

class NPOBase(BaseModel):
    """Base NPO schema."""
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10)
    email: EmailStr
    website: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    mission_statement: str = Field(..., min_length=20, max_length=500)
    registration_number: str = Field(..., min_length=5, max_length=50)
    xrpl_address: str
    categories: List[str] = Field(..., min_items=1)
    social_media_links: Optional[List[HttpUrl]] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    is_verified: bool = False


class NPOCreate(NPOBase):
    """Schema for creating an NPO."""
    admin_id: int


class NPOUpdate(BaseModel):
    """Schema for updating an NPO."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    mission_statement: Optional[str] = Field(None, min_length=20, max_length=500)
    xrpl_address: Optional[str] = None
    categories: Optional[List[str]] = Field(None, min_items=1)
    social_media_links: Optional[List[HttpUrl]] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None


class NPO(NPOBase):
    """Complete NPO schema."""
    id: int
    admin_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_donations_received: float = 0
    total_campaigns: int = 0
    active_campaigns: int = 0

    class Config:
        from_attributes = True 