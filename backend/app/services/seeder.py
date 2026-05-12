from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from sqlmodel import Session, select

from ..core.config import settings
from ..models.tour import Tour


def _find_seed_file() -> Path | None:
    p = Path(settings.seed_path)
    if p.is_absolute() and p.exists():
        return p
    candidates = [
        Path.cwd() / settings.seed_path,
        Path(__file__).resolve().parents[2] / settings.seed_path,
        Path(__file__).resolve().parents[3] / "contracts" / "tours_seed.json",
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    return None


def seed_tours(session: Session) -> int:
    existing = session.exec(select(Tour)).first()
    if existing is not None:
        return 0

    seed_file = _find_seed_file()
    if seed_file is None:
        return 0

    rows = json.loads(seed_file.read_text())
    for row in rows:
        session.add(
            Tour(
                title=row["title"],
                country=row["country"],
                city=row["city"],
                price=float(row["price"]),
                duration_days=int(row["duration_days"]),
                start_date=date.fromisoformat(row["start_date"]),
                end_date=date.fromisoformat(row["end_date"]),
                description=row["description"],
                image_url=row["image_url"],
                rating=float(row.get("rating", 0.0)),
                available_slots=int(row.get("available_slots", 0)),
            )
        )
    session.commit()
    return len(rows)
