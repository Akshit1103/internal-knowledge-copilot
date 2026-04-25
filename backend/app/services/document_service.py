from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Document, User
from app.schemas.documents import ChunkSummary, DocumentListResponse, DocumentResponse, UploadResult
from app.services.audit_service import write_audit_log
from app.services.ingestion_service import IngestionService


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.ingestion = IngestionService(db)

    def list_documents(self) -> DocumentListResponse:
        items = self.db.query(Document).order_by(Document.upload_date.desc()).all()
        return DocumentListResponse(items=items)

    def get_document(self, document_id: int) -> DocumentResponse:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")
        return DocumentResponse(
            id=document.id,
            title=document.title,
            filename=document.filename,
            document_type=document.document_type,
            department=document.department,
            version=document.version,
            approved=document.approved,
            upload_date=document.upload_date,
            chunks=[
                ChunkSummary(id=chunk.id, chunk_index=chunk.chunk_index, preview=chunk.content[:200])
                for chunk in document.chunks
            ],
        )

    def ingest_upload(
        self,
        *,
        filename: str,
        content: bytes,
        uploaded_by: User,
        department: str,
        version: str,
        document_type: str,
        approved: bool,
    ) -> UploadResult:
        Path(self.settings.upload_dir).mkdir(parents=True, exist_ok=True)
        text = self.ingestion.extract_text(filename, content)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract any text from the uploaded file.")
        result = self.ingestion.ingest_text(
            filename=filename,
            title=Path(filename).stem.replace("_", " ").title(),
            text=text,
            uploaded_by=uploaded_by,
            department=department,
            version=version,
            document_type=document_type,
            approved=approved,
        )
        write_audit_log(
            self.db,
            actor=uploaded_by,
            action="document.upload",
            entity_type="document",
            entity_id=str(result.document_id),
            details={"filename": filename, "department": department, "version": version},
        )
        self.db.commit()
        return result
