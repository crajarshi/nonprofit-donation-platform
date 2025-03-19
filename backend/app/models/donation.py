from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base_class import Base

class Donation(Base):
    __tablename__ = "donations"

    id = Column(String, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    donor_id = Column(String, ForeignKey("users.id"))
    npo_id = Column(String, ForeignKey("npos.id"))
    transaction_hash = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships will be added later to avoid circular imports
    # donor = relationship("User", back_populates="donations")
    # npo = relationship("NPO", back_populates="received_donations") 