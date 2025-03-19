from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.encoders import jsonable_encoder

from app.models.campaign import Campaign
from app.models.npo import NPO
from app.core.config import settings


def get_campaign(db: Session, id: int) -> Optional[Campaign]:
    """
    Get a campaign by ID.
    """
    return db.query(Campaign).filter(Campaign.id == id).first()


def get_campaigns(
    db: Session, 
    *, 
    skip: int = 0, 
    limit: int = 100,
    npo_id: Optional[int] = None,
    active_only: bool = False,
) -> List[Campaign]:
    """
    Get a list of campaigns with optional filtering.
    """
    query = db.query(Campaign)
    
    if npo_id is not None:
        query = query.filter(Campaign.npo_id == npo_id)
    
    if active_only:
        now = datetime.utcnow()
        query = query.filter(
            Campaign.start_date <= now,
            Campaign.end_date >= now
        )
    
    return query.offset(skip).limit(limit).all()


def create_campaign(
    db: Session, *, obj_in: Dict[str, Any]
) -> Campaign:
    """
    Create a new campaign.
    """
    obj_in_data = jsonable_encoder(obj_in)
    
    # Verify NPO exists
    npo = db.query(NPO).filter(NPO.id == obj_in_data["npo_id"]).first()
    if not npo:
        raise ValueError("NPO not found")
    
    db_obj = Campaign(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Update NPO stats
    npo.total_campaigns += 1
    db.add(npo)
    db.commit()
    
    return db_obj


def update_campaign(
    db: Session, *, db_obj: Campaign, obj_in: Dict[str, Any]
) -> Campaign:
    """
    Update a campaign.
    """
    obj_data = jsonable_encoder(db_obj)
    
    # Verify NPO exists if npo_id is being updated
    if "npo_id" in obj_in and obj_in["npo_id"] != db_obj.npo_id:
        npo = db.query(NPO).filter(NPO.id == obj_in["npo_id"]).first()
        if not npo:
            raise ValueError("NPO not found")
        
        # Update old and new NPO stats
        old_npo = db.query(NPO).filter(NPO.id == db_obj.npo_id).first()
        if old_npo:
            old_npo.total_campaigns -= 1
            db.add(old_npo)
        
        npo.total_campaigns += 1
        db.add(npo)
    
    for field in obj_data:
        if field in obj_in:
            setattr(db_obj, field, obj_in[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_campaign(db: Session, *, id: int) -> None:
    """
    Delete a campaign.
    """
    db_obj = db.query(Campaign).filter(Campaign.id == id).first()
    if db_obj:
        # Update NPO stats
        npo = db.query(NPO).filter(NPO.id == db_obj.npo_id).first()
        if npo:
            npo.total_campaigns -= 1
            db.add(npo)
        
        db.delete(db_obj)
        db.commit()


def check_campaign_status(db: Session) -> None:
    """
    Check and update campaign status based on end dates.
    """
    # Get all active campaigns with end dates in the past
    now = datetime.utcnow()
    expired_campaigns = (
        db.query(Campaign)
        .filter(Campaign.is_active == True)
        .filter(Campaign.end_date.isnot(None))
        .filter(Campaign.end_date < now)
        .all()
    )
    
    # Deactivate expired campaigns
    for campaign in expired_campaigns:
        campaign.is_active = False
        db.add(campaign)
    
    db.commit()


def get_campaigns_by_npo(
    db: Session, *, npo_id: int, skip: int = 0, limit: int = 100, active_only: bool = True
) -> List[Campaign]:
    """
    Get campaigns for a specific non-profit organization.
    """
    return get_campaigns(db, skip=skip, limit=limit, active_only=active_only, npo_id=npo_id)


def remove_campaign(db: Session, *, id: int) -> Campaign:
    """
    Remove a campaign.
    """
    obj = db.query(Campaign).get(id)
    
    # Update NPO stats
    npo = db.query(NPO).filter(NPO.id == obj.npo_id).first()
    if npo:
        npo.total_campaigns -= 1
        db.add(npo)
    
    db.delete(obj)
    db.commit()
    return obj 