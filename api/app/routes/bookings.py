from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Booking, User
from app.schemas import BookingCreate, BookingResponse
from app.services import booking_service
from app.security import get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.get("", response_model=list[BookingResponse])
def get_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (db.query(Booking).options(joinedload(Booking.customer)).all())
# Check behind the scenes what the SELECT query does. if it does SELECT * fix it to what you need and index on it

@router.post("", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return booking_service.create_booking(db, booking)
