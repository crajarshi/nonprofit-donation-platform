from datetime import datetime
from sqlalchemy import Boolean, Column, String, Integer, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from app.database.session import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Campaign media
    cover_image = Column(String, nullable=True)
    media_urls = Column(String, nullable=True)  # JSON string of URLs
    
    # Campaign goals and status
    goal_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Campaign rewards
    offers_nft = Column(Boolean, default=False)
    nft_details = Column(String, nullable=True)  # JSON string with NFT details
    governance_token = Column(Boolean, default=False)
    token_details = Column(String, nullable=True)  # JSON string with token details
    
    # Nonprofit organization that owns this campaign
    npo_id = Column(Integer, ForeignKey("non_profit_orgs.id"), nullable=False)
    npo = relationship("NonProfitOrg", back_populates="campaigns")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    donations = relationship("Donation", back_populates="campaign") 