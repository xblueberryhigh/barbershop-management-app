from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    BARBER = "barber"

class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    PENDING = "pending"
