"""LangChain tool agent backed by ChatOpenAI."""

from __future__ import annotations

import json
import logging
import queue
import threading
from collections.abc import Callable, Iterator
from datetime import date
from typing import Any, List, Literal, Optional, Tuple
from uuid import UUID

from sqlmodel import Session, select

from ..core.config import settings
from ..models.tour import Tour
from ..schemas.agent import AgentChatRequest, AgentChatResponse
from .heuristic_chat import heuristic_chat
from .prompts import AGENT_SYSTEM_PROMPT
from ..services.filters import query_tours

logger = logging.getLogger(__name__)

TOOL_STEP_LABELS: dict[str, str] = {
    "search_catalog": "Searching the live tour catalog…",
    "get_tour_details": "Loading tour details…",
    "list_destination_countries": "Gathering destinations we offer…",
}

SortPref = Literal["rating", "price_low", "price_high", "start_date"]
_SORT_PREF_TO_KEY: dict = {
    "rating": "rating_desc",
    "price_low": "price_asc",
    "price_high": "price_desc",
    "start_date": "date_asc",
}


def _tour_summaries(rows: List[Tour]) -> List[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for t in rows:
        start = (
            t.start_date.isoformat()
            if isinstance(t.start_date, date)
            else str(t.start_date)
        )
        end = (
            t.end_date.isoformat()
            if isinstance(t.end_date, date)
            else str(t.end_date)
        )
        out.append(
            {
                "id": str(t.id),
                "title": t.title,
                "country": t.country,
                "city": t.city,
                "price": float(t.price),
                "duration_days": t.duration_days,
                "start_date": start,
                "end_date": end,
                "rating": float(t.rating),
                "available_slots": int(t.available_slots),
                "description_excerpt": t.description[:400]
                + ("…" if len(t.description) > 400 else ""),
            }
        )
    return out


def _serialize_tour_detail(tour: Tour) -> dict[str, Any]:
    return {
        "id": str(tour.id),
        "title": tour.title,
        "country": tour.country,
        "city": tour.city,
        "price": float(tour.price),
        "duration_days": tour.duration_days,
        "start_date": tour.start_date.isoformat()
        if hasattr(tour.start_date, "isoformat")
        else str(tour.start_date),
        "end_date": tour.end_date.isoformat()
        if hasattr(tour.end_date, "isoformat")
        else str(tour.end_date),
        "description": tour.description,
        "rating": float(tour.rating),
        "available_slots": int(tour.available_slots),
        "image_url": tour.image_url,
    }


def _collect_ids_from_intermediate(
    intermediate_steps: Optional[List[Tuple[Any, Any]]],
) -> List[str]:
    ids: List[str] = []
    if not intermediate_steps:
        return ids
    for _action, observation in intermediate_steps:
        raw = observation if isinstance(observation, str) else str(observation)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        chunks: List[Any]
        if isinstance(data, dict) and data.get("_type") == "single":
            chunks = [data.get("tour")] if isinstance(data.get("tour"), dict) else []
        elif isinstance(data, list):
            chunks = data
        elif isinstance(data, dict):
            chunks = [data]
        else:
            chunks = []
        for row in chunks:
            if isinstance(row, dict) and row.get("id"):
                sid = str(row["id"])
                if sid not in ids:
                    ids.append(sid)
    return ids[:3]


def _build_tools(session: Session) -> List[Any]:
    from langchain_core.tools import tool

    @tool("search_catalog")
    def search_catalog(
        country: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        date_from_iso: Optional[str] = None,
        date_to_iso: Optional[str] = None,
        keyword: Optional[str] = None,
        sort_preference: SortPref = "rating",
        limit: int = 12,
    ) -> str:
        """Search the live tour inventory. Combines structured filters with OR-style keyword overlap on title/city/description."""
        pf: Optional[date] = None
        pt: Optional[date] = None
        if date_from_iso:
            try:
                pf = date.fromisoformat(date_from_iso)
            except ValueError:
                pass
        if date_to_iso:
            try:
                pt = date.fromisoformat(date_to_iso)
            except ValueError:
                pass
        fetch_size = max(40, min(100, limit * 8))
        items, _total, _page, _size = query_tours(
            session,
            country=country,
            price_min=float(price_min) if price_min is not None else None,
            price_max=float(price_max) if price_max is not None else None,
            date_from=pf,
            date_to=pt,
            sort=_SORT_PREF_TO_KEY.get(sort_preference, "rating_desc"),
            page=1,
            size=fetch_size,
        )
        if keyword:
            k = keyword.lower()
            items = [
                t
                for t in items
                if k in t.title.lower()
                or k in t.city.lower()
                or k in t.country.lower()
                or k in t.description.lower()
            ]
        rows = items[: max(1, min(20, limit))]
        summary = _tour_summaries(rows)
        return json.dumps(summary, ensure_ascii=False)

    @tool("get_tour_details")
    def get_tour_details(tour_id: str) -> str:
        """Return one tour by UUID string (canonical catalog row)."""
        try:
            key = UUID(tour_id.strip())
        except ValueError:
            return json.dumps({"error": "invalid_tour_id"})
        tour = session.get(Tour, key)
        if tour is None:
            return json.dumps({"error": "not_found", "id": tour_id})
        wrapped = {"_type": "single", "tour": _serialize_tour_detail(tour)}
        return json.dumps(wrapped, ensure_ascii=False)

    @tool("list_destination_countries")
    def list_destination_countries() -> str:
        """Distinct countries offered in inventory, sorted alphabetically."""
        rows = session.exec(
            select(Tour.country).distinct().order_by(Tour.country)
        ).all()
        items = sorted({str(r).strip() for r in rows if r})
        return json.dumps(items, ensure_ascii=False)

    return [search_catalog, get_tour_details, list_destination_countries]


class _AgentToolStepEmitter:
    """Callback that surfaces tool calls as human-readable progress (stream UI)."""

    def __init__(self, sink: Callable[[str], None]) -> None:
        self._sink = sink

    def to_handler(self):  # noqa: ANN202 - langchain type is verbose
        from langchain_core.callbacks import BaseCallbackHandler

        outer = self

        class _H(BaseCallbackHandler):
            def on_tool_start(self, serialized: dict[str, Any], **kwargs: Any) -> Any:  # type: ignore[override]
                name = serialized.get("name")
                if not name and isinstance(serialized.get("id"), list):
                    tail = serialized["id"]
                    name = str(tail[-1]) if tail else ""
                label = TOOL_STEP_LABELS.get(str(name), f"Consulting inventory ({name})…")
                outer._sink(label)

        return _H()


def run_langchain_agent(
    session: Session,
    body: AgentChatRequest,
    *,
    on_tool_step: Optional[Callable[[str], None]] = None,
) -> Optional[AgentChatResponse]:
    key = settings.openai_api_key
    if not key or not str(key).strip():
        return None

    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=key,
        temperature=0.2,
    )

    tools = _build_tools(session)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", AGENT_SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=10,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )

    invoke_config: dict[str, Any] = {}
    if on_tool_step is not None:
        invoke_config["callbacks"] = [_AgentToolStepEmitter(on_tool_step).to_handler()]

    try:
        if invoke_config:
            result = executor.invoke({"input": body.message}, config=invoke_config)
        else:
            result = executor.invoke({"input": body.message})
    except Exception:
        logger.exception("LangChain agent invoke failed")
        return None

    reply = result.get("output")
    reply_text = (reply.strip() if isinstance(reply, str) else "") or (
        "I could not formulate a reply. Please try again in a moment."
    )

    suggested = _collect_ids_from_intermediate(
        result.get("intermediate_steps")  # type: ignore[arg-type]
    )

    return AgentChatResponse(reply=reply_text, suggested_tour_ids=suggested)


def finalize_assistant_response(
    session: Session,
    body: AgentChatRequest,
    llm_result: Optional[AgentChatResponse],
) -> AgentChatResponse:
    if llm_result is None:
        return heuristic_chat(session, body)
    if not llm_result.suggested_tour_ids:
        heur = heuristic_chat(session, body)
        merged_ids = llm_result.suggested_tour_ids + heur.suggested_tour_ids
        uniq: List[str] = []
        for tid in merged_ids:
            if tid not in uniq:
                uniq.append(tid)
            if len(uniq) >= 3:
                break
        return AgentChatResponse(
            reply=llm_result.reply,
            suggested_tour_ids=uniq,
        )
    return llm_result


def assistant_reply(session: Session, body: AgentChatRequest) -> AgentChatResponse:
    return finalize_assistant_response(session, body, run_langchain_agent(session, body))


def _sse_pack(obj: dict[str, Any]) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


def agent_chat_sse_events(session: Session, body: AgentChatRequest) -> Iterator[str]:
    """SSE stream: `step` events with human-readable progress, final `done` with full reply."""
    if not settings.openai_api_key or not str(settings.openai_api_key).strip():
        yield _sse_pack(
            {"event": "step", "detail": "Matching tours against your filters…"}
        )
        finalized = heuristic_chat(session, body)
        yield _sse_pack({"event": "done", **finalized.model_dump()})
        return

    q: queue.Queue[tuple[str, Any]] = queue.Queue()

    def worker() -> None:
        try:

            def emit(step: str) -> None:
                q.put(("step", step))

            llm_resp = run_langchain_agent(session, body, on_tool_step=emit)
            q.put(("final", llm_resp))
        except Exception as exc:  # noqa: BLE001
            logger.exception("LangChain SSE worker failed")
            q.put(("error", str(exc)))

    yield _sse_pack({"event": "step", "detail": "Reading your request…"})
    yield _sse_pack({"event": "step", "detail": "Planning with AI…"})
    threading.Thread(target=worker, daemon=True).start()

    saw_tool = False
    while True:
        kind, payload = q.get()
        if kind == "step":
            saw_tool = True
            yield _sse_pack({"event": "step", "detail": str(payload)})
        elif kind == "final":
            if not saw_tool:
                yield _sse_pack(
                    {
                        "event": "step",
                        "detail": "Putting recommendations into words…",
                    }
                )
            finalized = finalize_assistant_response(session, body, payload)
            yield _sse_pack({"event": "done", **finalized.model_dump()})
            break
        elif kind == "error":
            yield _sse_pack({"event": "error", "message": str(payload)})
            break
