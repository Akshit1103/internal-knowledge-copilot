from __future__ import annotations

import json
import zipfile
from io import BytesIO

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Document, DocumentChunk, User
from app.schemas.documents import UploadResult
from app.services.vector_service import chunk_text, embed_text


class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def extract_text(self, filename: str, content: bytes) -> str:
        suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if suffix in {"txt", "md"}:
            return content.decode("utf-8", errors="ignore")
        if suffix == "docx":
            return self._extract_docx_text(content)
        if suffix == "pdf":
            return content.decode("utf-8", errors="ignore")
        return content.decode("utf-8", errors="ignore")

    def ingest_text(
        self,
        *,
        filename: str,
        title: str,
        text: str,
        uploaded_by: User,
        department: str,
        version: str,
        document_type: str,
        approved: bool,
    ) -> UploadResult:
        document = Document(
            title=title,
            filename=filename,
            document_type=document_type,
            department=department,
            version=version,
            approved=approved,
            uploaded_by_id=uploaded_by.id,
            raw_text=text,
        )
        self.db.add(document)
        self.db.flush()

        chunks = chunk_text(text, self.settings.chunk_size, self.settings.chunk_overlap)
        for index, item in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=item,
                embedding=json.dumps(embed_text(item, self.settings.embedding_dimensions)),
            )
            self.db.add(chunk)
        self.db.flush()
        return UploadResult(
            document_id=document.id,
            title=document.title,
            chunks_created=len(chunks),
            upload_date=document.upload_date,
        )

    def _extract_docx_text(self, content: bytes) -> str:
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
        except Exception:
            return ""
        return (
            xml.replace("</w:p>", "\n")
            .replace("</w:t>", " ")
            .replace("<w:t>", "")
            .replace("<w:p>", "")
        )
