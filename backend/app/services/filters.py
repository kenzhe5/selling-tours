from datetime import date
from typing import Optional

from sqlmodel import Session, func, select

from ..models.tour import Tour

_SORT_OPTIONS = {
    "price_asc": (Tour.price, "asc"),
    "price_desc": (Tour.price, "desc"),
    "rating_desc": (Tour.rating, "desc"),
    "date_asc": (Tour.start_date, "asc"),
}


def query_tours(
    session: Session,
    country: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[Tour], int, int, int]:
    where_clauses = []
    if country:
        where_clauses.append(Tour.country == country)
    if price_min is not None:
        where_clauses.append(Tour.price >= price_min)
    if price_max is not None:
        where_clauses.append(Tour.price <= price_max)
    if date_from is not None:
        where_clauses.append(Tour.start_date >= date_from)
    if date_to is not None:
        where_clauses.append(Tour.start_date <= date_to)

    count_stmt = select(func.count(Tour.id))
    for c in where_clauses:
        count_stmt = count_stmt.where(c)
    total = session.exec(count_stmt).one() or 0

    stmt = select(Tour)
    for c in where_clauses:
        stmt = stmt.where(c)

    if sort and sort in _SORT_OPTIONS:
        col_obj, direction = _SORT_OPTIONS[sort]
        stmt = stmt.order_by(col_obj.desc() if direction == "desc" else col_obj.asc())
    else:
        stmt = stmt.order_by(Tour.start_date.asc())

    page = max(1, page)
    size = min(max(1, size), 100)
    stmt = stmt.offset((page - 1) * size).limit(size)

    items = list(session.exec(stmt).all())
    return items, int(total), page, size
