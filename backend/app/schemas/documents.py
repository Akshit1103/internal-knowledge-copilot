from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChunkSummary(BaseModel):
    id: int
    chunk_index: int
    preview: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    document_type: str
    department: str
    version: str
    approved: bool
    upload_date: datetime
    chunks: list[ChunkSummary]


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    filename: str
    document_type: str
    department: str
    version: str
    approved: bool
    upload_date: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentListItem]


class UploadResult(BaseModel):
    document_id: int
    title: str
    chunks_created: int
    upload_date: datetime
