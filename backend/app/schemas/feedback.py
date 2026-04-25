from datetime import datetime

from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    chat_query_id: int
    rating: str
    notes: str | None = None


class FeedbackResponse(BaseModel):
    id: int
    chat_query_id: int
    rating: str
    notes: str | None
    created_at: datetime
