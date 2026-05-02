from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import UserRole
from app.models import User
from app.schemas import AssignableUserResponse, UserResponse
from app.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can get users")

    return db.query(User).order_by(User.id.asc()).all()


@router.get("/assignable-users", response_model=list[AssignableUserResponse])
def get_assignable_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user

    return db.query(User).filter(User.role == UserRole.BARBER).order_by(User.id.asc()).all()
