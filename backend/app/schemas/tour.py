from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TourRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    country: str
    city: str
    price: float
    duration_days: int
    start_date: date
    end_date: date
    description: str
    image_url: str
    rating: float
    available_slots: int


class TourList(BaseModel):
    items: list[TourRead]
    total: int
    page: int
    size: int
