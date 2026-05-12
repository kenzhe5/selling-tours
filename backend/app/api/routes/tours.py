from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ...core.db import get_session
from ...models.tour import Tour
from ...schemas.tour import TourList, TourRead
from ...services.filters import query_tours

router = APIRouter()


@router.get("/tours", response_model=TourList)
def list_tours(
    country: Optional[str] = None,
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort: Optional[str] = Query(
        None, pattern="^(price_asc|price_desc|rating_desc|date_asc)$"
    ),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> TourList:
    items, total, page, size = query_tours(
        session,
        country=country,
        price_min=price_min,
        price_max=price_max,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
        page=page,
        size=size,
    )
    return TourList(
        items=[TourRead.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/tours/{tour_id}", response_model=TourRead)
def get_tour(tour_id: UUID, session: Session = Depends(get_session)) -> Tour:
    tour = session.get(Tour, tour_id)
    if tour is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "tour_not_found", "message": "Tour not found"},
        )
    return tour
