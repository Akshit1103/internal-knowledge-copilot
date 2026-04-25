from sqlalchemy.orm import Session

from app.db.models import Feedback, User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.audit_service import write_audit_log


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def submit(self, payload: FeedbackCreate, user: User) -> FeedbackResponse:
        feedback = Feedback(
            chat_query_id=payload.chat_query_id,
            user_id=user.id,
            rating=payload.rating,
            notes=payload.notes,
        )
        self.db.add(feedback)
        self.db.flush()
        write_audit_log(
            self.db,
            actor=user,
            action="feedback.submit",
            entity_type="feedback",
            entity_id=str(feedback.id),
            details={"chat_query_id": payload.chat_query_id, "rating": payload.rating},
        )
        self.db.commit()
        return FeedbackResponse(
            id=feedback.id,
            chat_query_id=feedback.chat_query_id,
            rating=feedback.rating,
            notes=feedback.notes,
            created_at=feedback.created_at,
        )
