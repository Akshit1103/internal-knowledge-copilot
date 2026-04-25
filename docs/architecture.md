# Architecture

## Overview

The project will use a separated frontend and backend architecture with a local-first demo stack that can later be upgraded to managed services.

## Backend

- Framework: FastAPI
- Database: SQLite via SQLAlchemy for local development
- Vector layer: local vector store abstraction for document chunks and search
- LLM layer: provider wrapper with deterministic fallback for offline demos
- Observability: persisted query logs, retrieval logs, feedback, and latency tracking

## Frontend

- Framework: Next.js with App Router
- UI: dashboard-style layout with role-aware sections
- Screens:
  - sign in
  - overview dashboard
  - knowledge base library
  - chat workspace
  - admin analytics

## Data Domains

- users
- sessions
- documents
- document chunks
- chat queries
- chat responses
- feedback events
- audit logs

## Request Flow

1. User signs in and receives a role-aware session.
2. Admin uploads a document and metadata.
3. Backend extracts text, chunks content, creates embeddings, and stores searchable chunks.
4. User submits a natural-language question.
5. Backend retrieves top matching chunks, builds a grounded prompt, and produces a structured response.
6. UI renders answer, citations, confidence, follow-ups, and action items.
7. Feedback and audit events are stored for later review.
