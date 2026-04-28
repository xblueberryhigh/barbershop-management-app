from app.database import Base
from app.enums import BookingStatus, UserRole
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


enum_values = lambda enum_cls: [member.value for member in enum_cls]

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(
        SQLEnum(UserRole, native_enum=False, values_callable=enum_values),
        nullable=False,
    )
    bookings = relationship("Booking", back_populates="barber")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)

    bookings = relationship("Booking", back_populates="customer", cascade="all, delete-orphan")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    barber_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(
        SQLEnum(BookingStatus, native_enum=False, values_callable=enum_values),
        nullable=False,
    )

    customer = relationship("Customer", back_populates="bookings")
    barber = relationship("User", back_populates="bookings")
