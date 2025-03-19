from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services import npo_service, user_service

router = APIRouter()

@router.get("/npos/pending", response_model=List[schemas.NPO])
def get_pending_npos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get a list of non-profit organizations pending verification.
    """
    npos = npo_service.get_npos(db, skip=skip, limit=limit, verified_only=False)
    return [npo for npo in npos if not npo.is_verified]

@router.post("/npos/{npo_id}/verify", response_model=schemas.NPO)
def verify_npo(
    npo_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Verify a non-profit organization.
    """
    npo = npo_service.get_npo(db, id=npo_id)
    if not npo:
        raise HTTPException(
            status_code=404,
            detail="Non-profit organization not found",
        )
    
    npo = npo_service.update_npo(
        db,
        db_obj=npo,
        obj_in={"is_verified": True}
    )
    return npo

@router.post("/users/{user_id}/superuser", response_model=schemas.User)
def make_user_superuser(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Make a user a superuser.
    """
    user = user_service.get_user(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    
    user = user_service.update_user(
        db,
        db_obj=user,
        obj_in={"is_superuser": True}
    )
    return user

@router.post("/users/{user_id}/deactivate", response_model=schemas.User)
def deactivate_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Deactivate a user.
    """
    user = user_service.get_user(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    
    user = user_service.update_user(
        db,
        db_obj=user,
        obj_in={"is_active": False}
    )
    return user 