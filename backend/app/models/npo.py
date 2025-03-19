from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base_class import Base

if TYPE_CHECKING:
    from .donation import Donation  # noqa: F401
    from .campaign import Campaign  # noqa: F401

class NPO(Base):
    __tablename__ = "npos"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    email = Column(String, unique=True, index=True)
    website = Column(String)
    logo_url = Column(String)
    mission_statement = Column(String)
    registration_number = Column(String, unique=True)
    xrpl_address = Column(String, unique=True)
    categories = Column(String)  # Comma-separated list or JSON string
    social_media_links = Column(String)  # JSON string
    contact_phone = Column(String)
    contact_address = Column(String)
    is_verified = Column(Boolean, default=False)
    owner_id = Column(String, ForeignKey("users.id"))
    
    # Verification status
    verification_documents = Column(String)  # JSON string of document URLs
    
    # Statistics
    total_received = Column(Float, default=0.0)
    total_campaigns = Column(Integer, default=0)
    
    # Account creation and update timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_npo")
    # Temporarily comment out relationships until models are properly set up
    # received_donations = relationship("Donation", back_populates="npo")
    # campaigns = relationship("Campaign", back_populates="npo")

    def __repr__(self):
        return f"<NPO(name={self.name}, email={self.email}, xrpl_address={self.xrpl_address})>" 