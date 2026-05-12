from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookingCreate(BaseModel):
    tour_id: UUID
    user_name: str = Field(min_length=1, max_length=200)
    user_email: EmailStr
    start_date: date
    num_people: int = Field(ge=1, le=20)


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tour_id: UUID
    user_name: str
    user_email: EmailStr
    start_date: date
    num_people: int
    status: str
    created_at: datetime
