# Internal Knowledge Copilot

An enterprise-style AI knowledge assistant that lets teams upload internal documents, ask grounded questions, and review answers with sources, confidence, feedback, and audit logs.

## Project Goals

- Build a polished internal tool rather than a toy chatbot
- Keep `backend/` and `frontend/` separated for clear ownership
- Support document ingestion, semantic retrieval, grounded answers, and analytics
- Demonstrate production-style patterns: auth, roles, structured outputs, logs, and admin controls

## Planned Structure

```text
internal_knowledge_copilot/
├── backend/
├── docs/
└── frontend/
```

## Milestones

1. Project docs and repository setup
2. Backend scaffold with auth, documents, chat, feedback, and analytics APIs
3. Frontend scaffold with enterprise dashboard and chat experience
4. Retrieval pipeline and demo data
5. End-to-end verification and cleanup

## Initial Roles

- `admin`: upload and manage documents, view analytics
- `employee`: ask questions, view shared content, submit feedback
- `viewer`: read approved knowledge and chat responses only

## Core Demo Scope

- Local authentication with seeded users
- PDF, DOCX, Markdown, and text ingestion
- Chunking with metadata
- Vector-like retrieval for relevant passages
- Grounded structured answer responses
- Feedback capture and low-confidence review
- Audit-friendly logs and admin summaries
