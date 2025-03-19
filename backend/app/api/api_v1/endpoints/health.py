from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api import deps
from app.database.session import get_db

router = APIRouter()

@router.get("/health", response_model=Dict[str, str])
def health_check(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Health check endpoint.
    
    Checks:
    - API is running
    - Database connection is working
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)} 