from pydantic import BaseModel


class AgentChatRequest(BaseModel):
    session_id: str
    message: str


class AgentChatResponse(BaseModel):
    reply: str
    suggested_tour_ids: list[str]
