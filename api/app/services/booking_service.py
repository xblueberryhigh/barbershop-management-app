from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from app.models import Booking, Customer, User
from app.schemas import BookingCreate
from datetime import time, datetime

OPEN_TIME = time(8, 0)
BREAK_START = time(12, 0)
BREAK_END = time(14, 0)
CLOSE_TIME = time(23, 0)

WORKING_DAYS = {0, 1, 2, 3, 4}  # Monday-Friday

def create_booking(db: Session, booking: BookingCreate) -> Booking:
    get_customer_or_404(db, booking.customer_id)
    check_valid_booking_time(booking.start_time, booking.end_time)
    check_barber_exists(db, booking.barber_id)
    check_booking_conflict(db, booking.start_time, booking.end_time, booking.barber_id)

    new_booking = Booking(
        customer_id=booking.customer_id,
        barber_id=booking.barber_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=booking.status,
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return get_booking_with_relations(db, new_booking.id)

def get_customer_or_404(db: Session, customer_id: int) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

def get_booking_with_relations(db: Session, booking_id: int) -> Booking:
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.customer), joinedload(Booking.barber))
        .filter(Booking.id == booking_id)
        .first()
    )
    return booking

def check_valid_booking_time(start_time: datetime, end_time: datetime):
    if end_time <= start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    if start_time.date() != end_time.date():
        raise HTTPException(status_code=400, detail="Booking must start and end on the same day")

    if start_time.weekday() not in WORKING_DAYS:
        raise HTTPException(status_code=400, detail="Bookings are only allowed on working days")

    if end_time.weekday() not in WORKING_DAYS:
        raise HTTPException(status_code=400, detail="Bookings are only allowed on working days")

    if start_time < datetime.now():
        raise HTTPException(status_code=400, detail="Bookings cannot be created in the past")

    if start_time.time() < OPEN_TIME:
        raise HTTPException(status_code=400, detail="Booking cannot start before opening time")

    if end_time.time() > CLOSE_TIME:
        raise HTTPException(status_code=400, detail="Booking cannot end after closing time")

    if start_time.time() >= BREAK_START and start_time.time() < BREAK_END:
        raise HTTPException(status_code=400, detail="Booking cannot start during the lunch break")

    if end_time.time() > BREAK_START and end_time.time() <= BREAK_END:
        raise HTTPException(status_code=400, detail="Booking cannot end during the lunch break")

    if start_time.time() < BREAK_END and end_time.time() > BREAK_START:
        raise HTTPException(status_code=400, detail="Booking cannot overlap the lunch break")
    
def check_barber_exists(db: Session, barber_id: int):
    barber = db.query(User).filter(User.id == barber_id).first()

    if barber is None:
        raise HTTPException(status_code=404, detail="Barber not found")


def check_booking_conflict(db: Session, start_time: datetime, end_time: datetime, barber_id: int):
    conflict = (
        db.query(Booking.id)
        .filter(
            Booking.barber_id == barber_id,
            Booking.start_time < end_time,
            Booking.end_time > start_time,
        )
        .first()
    )
    if conflict is not None:
        raise HTTPException(status_code=400, detail="Booking conflicts with an existing booking")

