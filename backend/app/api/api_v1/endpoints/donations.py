from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services import donation_service, blockchain_service
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[schemas.Donation])
def list_donations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    campaign_id: Optional[int] = None,
    npo_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve donations.
    """
    if current_user.is_admin:
        # Admin can see all donations
        return donation_service.get_donations(
            db, skip=skip, limit=limit, campaign_id=campaign_id, npo_id=npo_id
        )
    else:
        # Regular users can only see their own donations
        return donation_service.get_user_donations(
            db, user_id=current_user.id, skip=skip, limit=limit,
            campaign_id=campaign_id, npo_id=npo_id
        )


@router.post("/initiate", response_model=schemas.DonationCreate)
async def initiate_donation(
    donation_in: schemas.DonationCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Initiate a new donation transaction.
    """
    # Validate the campaign and NPO
    campaign = donation_service.get_campaign(db, donation_in.campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    
    if not campaign.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign is not active",
        )
    
    # Prepare the donation transaction
    donation = donation_service.create_donation(
        db, 
        obj_in=donation_in, 
        donor_id=current_user.id if not donation_in.is_anonymous else None
    )
    
    # Initiate the blockchain transaction
    try:
        tx_result = await blockchain_service.initiate_xrp_payment(
            from_address=current_user.xrpl_address,
            to_address=campaign.npo.xrpl_address,
            amount=donation_in.amount,
            use_escrow=donation_in.use_escrow,
        )
        
        # Update the donation with transaction details
        donation_update = schemas.DonationUpdate(
            tx_hash=tx_result.get("tx_hash"),
            escrow_id=tx_result.get("escrow_id"),
            status="pending"
        )
        return donation_service.update_donation(db, db_obj=donation, obj_in=donation_update)
    except Exception as e:
        # Delete the donation if transaction fails
        donation_service.delete_donation(db, id=donation.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate donation: {str(e)}",
        )


@router.get("/{donation_id}", response_model=schemas.Donation)
def get_donation(
    donation_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get donation by ID.
    """
    donation = donation_service.get_donation(db, id=donation_id)
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donation not found",
        )
    
    # Check if the user has permission to view this donation
    if not current_user.is_admin and (
        (donation.donor_id is not None and donation.donor_id != current_user.id) and
        (current_user.owned_npo is None or donation.npo_id != current_user.owned_npo.id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this donation",
        )
    
    # Check blockchain status
    if donation.tx_hash and donation.status == "pending":
        tx_status = blockchain_service.check_transaction_status(donation.tx_hash)
        if tx_status != donation.status:
            donation_update = schemas.DonationUpdate(status=tx_status)
            if tx_status == "completed":
                donation_update.completed_at = datetime.utcnow()
            donation = donation_service.update_donation(db, db_obj=donation, obj_in=donation_update)
    
    return donation 