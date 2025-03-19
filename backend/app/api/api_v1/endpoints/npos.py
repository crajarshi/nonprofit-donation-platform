from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services import npo_service
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[schemas.NPO])
def read_npos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve non-profit organizations.
    """
    npos = npo_service.get_npos(
        db, skip=skip, limit=limit, verified_only=True
    )
    return npos


@router.post("/", response_model=schemas.NPO)
def create_npo(
    *,
    db: Session = Depends(deps.get_db),
    npo_in: schemas.NPOCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Create new non-profit organization.
    """
    # Check if user already owns an NPO
    if current_user.owned_npo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already owns a non-profit organization",
        )
    
    # Check if NPO with the same name exists
    if npo_service.get_npo_by_name(db, name=npo_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non-profit organization with this name already exists",
        )
    
    # Create the NPO
    return npo_service.create_npo(db, obj_in=npo_in, owner_id=current_user.id)


@router.get("/{npo_id}", response_model=schemas.NPO)
def read_npo(
    *,
    db: Session = Depends(deps.get_db),
    npo_id: int,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get non-profit organization by ID.
    """
    npo = npo_service.get_npo(db, id=npo_id)
    if not npo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-profit organization not found",
        )
    return npo


@router.put("/{npo_id}", response_model=schemas.NPO)
def update_npo(
    *,
    db: Session = Depends(deps.get_db),
    npo_id: int,
    npo_in: schemas.NPOUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Update a non-profit organization.
    """
    npo = npo_service.get_npo(db, id=npo_id)
    if not npo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-profit organization not found",
        )
    
    # Check if user is the owner or an admin
    if npo.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this non-profit organization",
        )
    
    # Prevent users from self-verifying
    if not current_user.is_admin and npo_in.is_verified is not None:
        npo_in.is_verified = npo.is_verified
    
    return npo_service.update_npo(db, db_obj=npo, obj_in=npo_in)


@router.post("/{npo_id}/proof", response_model=schemas.NPO)
def submit_proof(
    npo_id: int,
    proof_description: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    proof_file: UploadFile = File(...),
):
    """
    Submit proof of fund utilization.
    """
    npo = npo_service.get_npo(db, id=npo_id)
    if not npo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-profit organization not found",
        )
    
    # Check if user is the owner
    if npo.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to submit proof for this non-profit organization",
        )
    
    # Upload proof file to S3
    proof_url = npo_service.upload_proof_file(proof_file, npo_id)
    
    # Update NPO with proof information
    return npo_service.add_proof(db, npo=npo, description=proof_description, url=proof_url)


@router.get("/{npo_id}/campaigns", response_model=List[schemas.Campaign])
def get_npo_campaigns(
    npo_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
):
    """
    Get campaigns for a specific non-profit organization.
    """
    npo = npo_service.get_npo(db, id=npo_id)
    if not npo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-profit organization not found",
        )
    
    return npo_service.get_npo_campaigns(
        db, npo_id=npo_id, skip=skip, limit=limit, active_only=active_only
    )


@router.delete("/{npo_id}", response_model=schemas.NPO)
def delete_npo(
    *,
    db: Session = Depends(deps.get_db),
    npo_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Delete a non-profit organization.
    """
    npo = npo_service.get_npo(db, id=npo_id)
    if not npo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-profit organization not found",
        )
    return npo_service.remove_npo(db, id=npo_id) 