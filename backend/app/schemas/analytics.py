from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
    total_feedback: int
    low_confidence_queries: int
    helpful_feedback: int
    incorrect_feedback: int
    incomplete_feedback: int
