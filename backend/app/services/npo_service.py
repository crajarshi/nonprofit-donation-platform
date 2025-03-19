import uuid
import boto3
from typing import Any, Dict, List, Optional, Union
from fastapi import UploadFile
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from datetime import datetime

from app.models.npo import NPO
from app.models.campaign import Campaign
from app.core.config import settings


def get_npo(db: Session, id: int) -> Optional[NPO]:
    """
    Get a non-profit organization by ID.
    """
    return db.query(NPO).filter(NPO.id == id).first()


def get_npo_by_name(db: Session, name: str) -> Optional[NPO]:
    """
    Get a non-profit organization by name.
    """
    return db.query(NPO).filter(NPO.name == name).first()


def get_npos(
    db: Session, 
    *, 
    skip: int = 0, 
    limit: int = 100,
    verified_only: bool = True
) -> List[NPO]:
    """
    Get multiple non-profit organizations with optional filtering.
    """
    query = db.query(NPO)
    
    if verified_only:
        query = query.filter(NPO.is_verified == True)
    
    return query.offset(skip).limit(limit).all()


def create_npo(
    db: Session, *, obj_in: Dict[str, Any]
) -> NPO:
    """
    Create a new non-profit organization.
    """
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = NPO(**obj_in_data)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_npo(
    db: Session, *, db_obj: NPO, obj_in: Union[Dict[str, Any], Any]
) -> NPO:
    """
    Update a non-profit organization.
    """
    obj_data = jsonable_encoder(db_obj)
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def upload_proof_file(proof_file: UploadFile, npo_id: int) -> str:
    """
    Upload a proof file to S3 and return the URL.
    """
    # Generate a unique filename
    file_extension = proof_file.filename.split(".")[-1]
    filename = f"proofs/{npo_id}/{uuid.uuid4()}.{file_extension}"
    
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    # Upload the file
    s3_client.upload_fileobj(
        proof_file.file,
        settings.S3_BUCKET,
        filename,
        ExtraArgs={"ContentType": proof_file.content_type}
    )
    
    # Return the URL
    url = f"https://{settings.S3_BUCKET}.s3.amazonaws.com/{filename}"
    return url


def add_proof(
    db: Session, *, npo: NPO, description: str, url: str
) -> NPO:
    """
    Add a proof of fund utilization.
    """
    # Here we would normally store this in a separate proof table
    # For simplicity, we'll just update the NPO with the URL
    # In a real implementation, this should be a separate model
    
    # Update the NPO
    npo.verification_documents = url
    db.add(npo)
    db.commit()
    db.refresh(npo)
    return npo


def get_npo_campaigns(
    db: Session, 
    *, 
    npo_id: int,
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = True
) -> List[Campaign]:
    """
    Get campaigns for a specific non-profit organization.
    """
    query = db.query(Campaign).filter(Campaign.npo_id == npo_id)
    
    if active_only:
        query = query.filter(Campaign.is_active == True)
    
    return query.offset(skip).limit(limit).all()


def get_npo_by_owner(db: Session, owner_id: int) -> Optional[NPO]:
    """
    Get a non-profit organization by owner ID.
    """
    return db.query(NPO).filter(NPO.owner_id == owner_id).first()


def remove_npo(db: Session, *, id: int) -> NPO:
    """
    Remove a non-profit organization.
    """
    obj = db.query(NPO).get(id)
    db.delete(obj)
    db.commit()
    return obj 