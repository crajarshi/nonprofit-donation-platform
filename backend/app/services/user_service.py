from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from app.core.security import verify_password, get_password_hash
from app.models.user import User


def get_user(db: Session, id: int) -> Optional[User]:
    """
    Get a user by ID.
    """
    return db.query(User).filter(User.id == id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.
    """
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[User]:
    """
    Get multiple users.
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, *, user_in: Dict[str, Any]) -> User:
    """
    Create a new user.
    """
    db_user = User(
        email=user_in["email"],
        hashed_password=get_password_hash(user_in["password"]),
        full_name=user_in.get("full_name"),
        is_admin=user_in.get("is_admin", False),
        is_active=user_in.get("is_active", True),
        xrpl_address=user_in.get("xrpl_address")
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, *, db_obj: User, obj_in: Union[Dict[str, Any], Any]
) -> User:
    """
    Update a user.
    """
    update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    for field in update_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def authenticate(
    db: Session, *, email: str, password: str
) -> Optional[User]:
    """
    Authenticate a user.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_active(user: User) -> bool:
    """
    Check if user is active.
    """
    return user.is_active


def is_admin(user: User) -> bool:
    """
    Check if user is admin.
    """
    return user.is_admin 