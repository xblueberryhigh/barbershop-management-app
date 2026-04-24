from fastapi import Depends, APIRouter
from app.schemas import CustomerCreate, CustomerResponse
from app.database import get_db
from app.models import Customer
from sqlalchemy.orm import Session


router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("", response_model=list[CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()

@router.post("", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    new_customer = Customer(
        first_name = customer.first_name,
        last_name = customer.last_name,
        phone_number = customer.phone_number
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer
