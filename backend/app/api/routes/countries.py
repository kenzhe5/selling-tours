from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...core.db import get_session
from ...models.tour import Tour

router = APIRouter()


@router.get("/countries")
def list_countries(session: Session = Depends(get_session)) -> dict[str, list[str]]:
    rows = session.exec(
        select(Tour.country).distinct().order_by(Tour.country)
    ).all()
    return {"items": list(rows)}
