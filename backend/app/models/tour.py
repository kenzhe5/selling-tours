from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Tour(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    country: str = Field(index=True)
    city: str
    price: float = Field(index=True)
    duration_days: int
    start_date: date = Field(index=True)
    end_date: date
    description: str
    image_url: str
    rating: float = 0.0
    available_slots: int = 0
    created_at: datetime = Field(default_factory=_utcnow)
