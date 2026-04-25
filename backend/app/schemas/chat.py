from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    department: str | None = None


class Citation(BaseModel):
    document_id: int
    document_title: str
    department: str
    version: str
    snippet: str
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    query_id: int
    answer: str
    citations: list[Citation]
    confidence: float
    follow_up_suggestions: list[str]
    action_items: list[str]
    fallback_used: bool
    answered_at: datetime
