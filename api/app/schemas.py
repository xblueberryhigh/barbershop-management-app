from datetime import datetime
from typing import Literal

from app.enums import BookingStatus, UserRole
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

class UserRegister(BaseModel):
    first_name: str = Field(min_length=2, max_length=30)
    last_name: str = Field(min_length=2, max_length=30)
    email: EmailStr
    password: str = Field(min_length=5, max_length=100)

    @field_validator("first_name", "last_name", "email", mode="before")
    @classmethod
    def strip_and_validate_strings(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Cannot be blank")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Cannot be blank")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=100)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Email cannot be blank")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Password cannot be blank")
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


class CustomerCreate(BaseModel):
    first_name: str = Field(min_length=2, max_length=30)
    last_name: str = Field(min_length=2, max_length=30)
    phone_number: str = Field(min_length=7, max_length=20)

    @field_validator("first_name", "last_name", "phone_number", mode="before")
    @classmethod
    def strip_and_validate_customer_strings(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Cannot be blank")
        return value


class BookingCreate(BaseModel):
    customer_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self
    
class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    last_name: str
    phone_number: str

class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    customer: CustomerResponse
    
