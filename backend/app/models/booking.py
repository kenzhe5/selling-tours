from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Booking(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tour_id: UUID = Field(foreign_key="tour.id", index=True)
    user_name: str
    user_email: str = Field(index=True)
    start_date: date
    num_people: int
    status: str = "confirmed"
    created_at: datetime = Field(default_factory=_utcnow)
