from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from app.models import Booking, Customer
from app.schemas import BookingCreate

def create_booking(db: Session, booking: BookingCreate) -> Booking:
    get_customer_or_404(db, booking.customer_id)

    new_booking = Booking(
        customer_id=booking.customer_id,
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
        .options(joinedload(Booking.customer))
        .filter(Booking.id == booking_id)
        .first()
    )
    return booking
