from __future__ import annotations

import json
import math
import re

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Document, DocumentChunk
from app.schemas.chat import Citation
from app.services.vector_service import embed_text


class RetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def search(self, question: str, department: str | None = None) -> list[Citation]:
        query_vector = embed_text(question, self.settings.embedding_dimensions)
        query = self.db.query(DocumentChunk).join(Document).filter(Document.approved.is_(True))
        if department:
            query = query.filter(Document.department == department)
        chunks = query.all()

        scored: list[Citation] = []
        for chunk in chunks:
            embedding_score = cosine_similarity(query_vector, json.loads(chunk.embedding))
            keyword_score = keyword_overlap(question, chunk.content)
            score = (embedding_score * 0.55) + (keyword_score * 0.45)
            scored.append(
                Citation(
                    document_id=chunk.document.id,
                    document_title=chunk.document.title,
                    department=chunk.document.department,
                    version=chunk.document.version,
                    snippet=chunk.content[:260].strip(),
                    chunk_index=chunk.chunk_index,
                    score=round(score, 2),
                )
            )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[: self.settings.retrieval_top_k]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    numerator = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return numerator / (norm_a * norm_b)


def keyword_overlap(question: str, content: str) -> float:
    question_tokens = set(re.findall(r"[a-zA-Z0-9]{3,}", question.lower()))
    content_tokens = set(re.findall(r"[a-zA-Z0-9]{3,}", content.lower()))
    if not question_tokens or not content_tokens:
        return 0.0
    shared = question_tokens & content_tokens
    return len(shared) / len(question_tokens)
