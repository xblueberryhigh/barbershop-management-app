from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Booking
from app.schemas import BookingCreate, BookingResponse
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.get("", response_model=list[BookingResponse])
def get_bookings(db: Session = Depends(get_db)):
    return (db.query(Booking).options(joinedload(Booking.customer)).all())
# Check behind the scenes what the SELECT query does. if it does SELECT * fix it to what you need and index on it

@router.post("", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    return booking_service.create_booking(db, booking)
