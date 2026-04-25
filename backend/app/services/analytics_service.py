from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import ChatQuery, Document, DocumentChunk, Feedback
from app.schemas.analytics import AnalyticsResponse


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def build_overview(self) -> AnalyticsResponse:
        helpful = self._count_feedback("helpful")
        incorrect = self._count_feedback("incorrect")
        incomplete = self._count_feedback("incomplete")
        return AnalyticsResponse(
            total_documents=self.db.query(func.count(Document.id)).scalar() or 0,
            total_chunks=self.db.query(func.count(DocumentChunk.id)).scalar() or 0,
            total_queries=self.db.query(func.count(ChatQuery.id)).scalar() or 0,
            total_feedback=self.db.query(func.count(Feedback.id)).scalar() or 0,
            low_confidence_queries=self.db.query(func.count(ChatQuery.id)).filter(ChatQuery.confidence < 0.45).scalar() or 0,
            helpful_feedback=helpful,
            incorrect_feedback=incorrect,
            incomplete_feedback=incomplete,
        )

    def _count_feedback(self, rating: str) -> int:
        return self.db.query(func.count(Feedback.id)).filter(Feedback.rating == rating).scalar() or 0
