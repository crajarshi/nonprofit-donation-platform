from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from fastapi.encoders import jsonable_encoder

from app.models.donation import Donation
from app.models.npo import NPO
from app.models.campaign import Campaign
from app.core.config import settings


def get_donation(db: Session, id: int) -> Optional[Donation]:
    """
    Get a donation by ID.
    """
    return db.query(Donation).filter(Donation.id == id).first()


def get_campaign(db: Session, id: int) -> Optional[Campaign]:
    """
    Get a campaign by ID.
    """
    return db.query(Campaign).filter(Campaign.id == id).first()


def get_donations(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    npo_id: Optional[int] = None,
    campaign_id: Optional[int] = None,
    donor_id: Optional[int] = None,
) -> List[Donation]:
    """
    Get a list of donations with optional filtering.
    """
    query = db.query(Donation)
    
    if npo_id is not None:
        query = query.filter(Donation.npo_id == npo_id)
    if campaign_id is not None:
        query = query.filter(Donation.campaign_id == campaign_id)
    if donor_id is not None:
        query = query.filter(Donation.donor_id == donor_id)
    
    return query.offset(skip).limit(limit).all()


def get_user_donations(
    db: Session, 
    *, 
    user_id: int,
    skip: int = 0, 
    limit: int = 100,
    campaign_id: Optional[int] = None,
    npo_id: Optional[int] = None
) -> List[Donation]:
    """
    Get donations for a specific user.
    """
    query = db.query(Donation).filter(Donation.donor_id == user_id)
    
    if campaign_id is not None:
        query = query.filter(Donation.campaign_id == campaign_id)
    
    if npo_id is not None:
        query = query.filter(Donation.npo_id == npo_id)
    
    return query.offset(skip).limit(limit).all()


def create_donation(
    db: Session,
    *,
    obj_in: Dict[str, Any],
    donor_id: int,
) -> Donation:
    """
    Create a new donation.
    """
    obj_in_data = jsonable_encoder(obj_in)
    obj_in_data["donor_id"] = donor_id
    obj_in_data["status"] = "pending"  # Initial status
    
    # Verify NPO exists
    npo = db.query(NPO).filter(NPO.id == obj_in_data["npo_id"]).first()
    if not npo:
        raise ValueError("NPO not found")
    
    # Verify campaign exists if provided
    if obj_in_data.get("campaign_id"):
        campaign = db.query(Campaign).filter(
            Campaign.id == obj_in_data["campaign_id"],
            Campaign.npo_id == obj_in_data["npo_id"]
        ).first()
        if not campaign:
            raise ValueError("Campaign not found or does not belong to the specified NPO")
    
    db_obj = Donation(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Update campaign amount if applicable
    if db_obj.campaign_id:
        campaign = get_campaign(db, id=db_obj.campaign_id)
        if campaign:
            campaign.current_amount += db_obj.amount
            db.add(campaign)
            db.commit()
    
    return db_obj


def update_donation(
    db: Session,
    *,
    db_obj: Donation,
    obj_in: Dict[str, Any],
) -> Donation:
    """
    Update a donation.
    """
    obj_data = jsonable_encoder(db_obj)
    
    for field in obj_data:
        if field in obj_in:
            setattr(db_obj, field, obj_in[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_donation(db: Session, *, id: int) -> None:
    """
    Delete a donation.
    """
    db_obj = db.query(Donation).filter(Donation.id == id).first()
    if db_obj:
        # Update campaign amount if applicable
        if db_obj.campaign_id and db_obj.status == "completed":
            campaign = get_campaign(db, id=db_obj.campaign_id)
            if campaign:
                campaign.current_amount -= db_obj.amount
                db.add(campaign)
        
        db.delete(db_obj)
        db.commit()
        
        
def process_donation_completion(db: Session, *, donation_id: int) -> Optional[Donation]:
    """
    Process a donation completion.
    """
    donation = get_donation(db, id=donation_id)
    if not donation:
        return None
    
    # Update donation status
    donation.status = "completed"
    donation.completed_at = datetime.utcnow()
    db.add(donation)
    
    # Update NPO stats
    if donation.npo_id:
        npo = db.query(NPO).filter(NPO.id == donation.npo_id).first()
        if npo:
            npo.total_received += donation.amount
            db.add(npo)
    
    db.commit()
    db.refresh(donation)
    return donation 