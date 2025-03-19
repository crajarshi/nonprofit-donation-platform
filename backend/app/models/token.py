from datetime import datetime
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from app.database.session import Base


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    
    # Token type
    token_type = Column(String, index=True)  # nft, governance_token
    
    # Token details
    token_id = Column(String, index=True, nullable=False)  # XRPL token identifier
    token_uri = Column(String, nullable=True)  # Metadata URI for NFTs
    token_amount = Column(Float, default=1.0)  # For fungible tokens
    
    # Token metadata (for NFTs)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    
    # Related donation information
    donation_id = Column(Integer, ForeignKey("donations.id"), nullable=True)
    
    # Token owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tokens")
    
    # Related NPO
    npo_id = Column(Integer, ForeignKey("non_profit_orgs.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Token status
    is_active = Column(Boolean, default=True)
    last_transferred_at = Column(DateTime, nullable=True)
    
    # Governance token voting rights
    governance_power = Column(Float, default=0.0)  # Only applicable for governance tokens 