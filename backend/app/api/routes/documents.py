from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.db.models import User
from app.schemas.documents import DocumentListResponse, DocumentResponse, UploadResult
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DocumentListResponse:
    require_role(user, "admin", "employee", "viewer")
    return DocumentService(db).list_documents()


@router.post("/upload", response_model=UploadResult)
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form(...),
    version: str = Form(default="1.0"),
    document_type: str = Form(default="policy"),
    approved: bool = Form(default=True),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UploadResult:
    require_role(user, "admin")
    content = await file.read()
    return DocumentService(db).ingest_upload(
        filename=file.filename or "untitled.txt",
        content=content,
        uploaded_by=user,
        department=department,
        version=version,
        document_type=document_type,
        approved=approved,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DocumentResponse:
    require_role(user, "admin", "employee", "viewer")
    return DocumentService(db).get_document(document_id)
