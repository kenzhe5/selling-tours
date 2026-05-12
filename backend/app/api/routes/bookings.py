from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ...core.db import get_session
from ...models.booking import Booking
from ...models.tour import Tour
from ...schemas.booking import BookingCreate, BookingRead

router = APIRouter()


@router.post("/bookings", response_model=BookingRead, status_code=201)
def create_booking(
    payload: BookingCreate,
    session: Session = Depends(get_session),
) -> Booking:
    tour = session.get(Tour, payload.tour_id)
    if tour is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "tour_not_found", "message": "Tour not found"},
        )
    if tour.available_slots < payload.num_people:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "no_slots",
                "message": "Not enough available slots for this tour",
                "details": {
                    "available_slots": tour.available_slots,
                    "requested": payload.num_people,
                },
            },
        )

    booking = Booking(
        tour_id=payload.tour_id,
        user_name=payload.user_name,
        user_email=str(payload.user_email),
        start_date=payload.start_date,
        num_people=payload.num_people,
    )
    tour.available_slots -= payload.num_people

    session.add(tour)
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


@router.get("/bookings", response_model=list[BookingRead])
def list_bookings(
    email: str = Query(..., description="User email to filter by"),
    session: Session = Depends(get_session),
) -> list[Booking]:
    stmt = (
        select(Booking)
        .where(Booking.user_email == email)
        .order_by(Booking.created_at.desc())
    )
    return list(session.exec(stmt).all())
