"""Rule-based replies when OPENAI_API_KEY is missing or the LLM path fails."""

from __future__ import annotations

from sqlmodel import Session, select

from ..models.tour import Tour
from ..schemas.agent import AgentChatRequest, AgentChatResponse


def heuristic_chat(
    session: Session,
    body: AgentChatRequest,
) -> AgentChatResponse:
    tours = list(session.exec(select(Tour).order_by(Tour.rating.desc())).all())
    if not tours:
        return AgentChatResponse(
            reply="The catalog is empty right now. Please try again later.",
            suggested_tour_ids=[],
        )

    normalized = body.message.lower()
    price_hint: str | None = None
    for token in normalized.replace(",", " ").split():
        if token.isdigit() and len(token) >= 2:
            price_hint = token
            break

    candidates: list[Tour] = []
    for tour in tours:
        if tour.country.lower() in normalized or tour.city.lower() in normalized:
            candidates.append(tour)
            continue
        title_words = [w for w in tour.title.lower().split() if len(w) > 3]
        if any(w in normalized for w in title_words):
            candidates.append(tour)
            continue
        if price_hint and str(int(tour.price)).startswith(price_hint[:2]):
            candidates.append(tour)

    suggestions = (candidates if candidates else tours[:2])[:3]
    titles = [t.title for t in suggestions]
    reply = (
        f"I would start with {titles[0]}. It lines up with common briefs and booking flow. "
        f"You can compare {len(suggestions)} suggested options below."
    )

    return AgentChatResponse(
        reply=reply,
        suggested_tour_ids=[str(t.id) for t in suggestions],
    )
