from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base_class import Base

if TYPE_CHECKING:
    from .npo import NPO  # noqa: F401
    from .donation import Donation  # noqa: F401

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_nonprofit = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    xrpl_address = Column(String, unique=True)

    # Relationships
    owned_npo = relationship("NPO", back_populates="owner", uselist=False)
    # Temporarily comment out donations relationship until Donation model is properly set up
    # donations = relationship("Donation", back_populates="donor") 