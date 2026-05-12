from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from ...ai.langchain_agent import agent_chat_sse_events, assistant_reply
from ...core.db import get_session
from ...schemas.agent import AgentChatRequest, AgentChatResponse

router = APIRouter()


@router.post("/agent/chat", response_model=AgentChatResponse)
def agent_chat(
    body: AgentChatRequest,
    session: Session = Depends(get_session),
) -> AgentChatResponse:
    return assistant_reply(session, body)


@router.post("/agent/chat/stream")
def agent_chat_stream(
    body: AgentChatRequest,
    session: Session = Depends(get_session),
) -> StreamingResponse:
    generator = agent_chat_sse_events(session, body)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
