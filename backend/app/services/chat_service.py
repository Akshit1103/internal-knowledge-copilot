from __future__ import annotations

import json
import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import ChatQuery, ChatResponseLog, User
from app.schemas.chat import ChatRequest, ChatResponse, Citation
from app.services.audit_service import write_audit_log
from app.services.retrieval_service import RetrievalService


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.retrieval_service = RetrievalService(db)

    def answer_question(self, payload: ChatRequest, user: User) -> ChatResponse:
        start = time.perf_counter()
        citations = self.retrieval_service.search(payload.question, payload.department)
        confidence = round(citations[0].score if citations else 0.0, 2)
        fallback_used = confidence < 0.35 or not citations
        answer = self._build_answer(payload.question, citations, fallback_used)
        follow_ups = self._build_follow_ups(citations, payload.department)
        action_items = self._build_action_items(citations, fallback_used)
        latency_ms = int((time.perf_counter() - start) * 1000)

        query = ChatQuery(
            user_id=user.id,
            question=payload.question,
            department_filter=payload.department,
            confidence=confidence,
            latency_ms=latency_ms,
        )
        self.db.add(query)
        self.db.flush()

        log = ChatResponseLog(
            chat_query_id=query.id,
            answer=answer,
            citations_json=json.dumps([item.model_dump() for item in citations]),
            suggestions_json=json.dumps(follow_ups),
            action_items_json=json.dumps(action_items),
            fallback_used=fallback_used,
        )
        self.db.add(log)
        write_audit_log(
            self.db,
            actor=user,
            action="chat.query",
            entity_type="chat_query",
            entity_id=str(query.id),
            details={"question": payload.question, "confidence": confidence, "latency_ms": latency_ms},
        )
        self.db.commit()

        return ChatResponse(
            query_id=query.id,
            answer=answer,
            citations=citations,
            confidence=confidence,
            follow_up_suggestions=follow_ups,
            action_items=action_items,
            fallback_used=fallback_used,
            answered_at=datetime.utcnow(),
        )

    def _build_answer(self, question: str, citations: list[Citation], fallback_used: bool) -> str:
        if fallback_used:
            return (
                f"I couldn't find strong enough support in the approved knowledge base to answer '{question}' with confidence. "
                "Please refine the question, narrow the department filter, or upload a more relevant document."
            )

        supporting_lines = []
        for item in citations[:3]:
            supporting_lines.append(
                f"{item.document_title} (v{item.version}, {item.department}) notes that {item.snippet}"
            )
        summary = " ".join(supporting_lines)
        return (
            "Based on the retrieved internal sources, "
            f"{summary} "
            "Use the cited documents as the primary source of truth for downstream decisions."
        )

    def _build_follow_ups(self, citations: list[Citation], department: str | None) -> list[str]:
        suggestions = [
            "Would you like a shorter policy summary?",
            "Should I pull the most relevant document sections only?",
            "Do you want this rewritten as action items for a teammate?",
        ]
        if department:
            suggestions.insert(0, f"Do you want me to keep future answers scoped to {department}?")
        elif citations:
            suggestions.insert(0, f"Should I focus only on {citations[0].department} guidance next?")
        return suggestions[:4]

    def _build_action_items(self, citations: list[Citation], fallback_used: bool) -> list[str]:
        if fallback_used:
            return [
                "Review whether an approved document covers this topic.",
                "Upload or approve a more relevant source document.",
                "Retry with a more specific question or department filter.",
            ]
        actions = []
        for item in citations[:3]:
            actions.append(f"Review {item.document_title} chunk {item.chunk_index} for implementation details.")
        return actions
