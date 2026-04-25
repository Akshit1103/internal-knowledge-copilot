from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import SessionLocal
from app.services.ingestion_service import IngestionService


DEFAULT_USERS = [
    {"name": "Ava Admin", "email": "admin@copilot.local", "password": "admin123", "role": "admin", "department": "Operations"},
    {"name": "Ethan Employee", "email": "employee@copilot.local", "password": "employee123", "role": "employee", "department": "People Ops"},
    {"name": "Vera Viewer", "email": "viewer@copilot.local", "password": "viewer123", "role": "viewer", "department": "Finance"},
]

DEMO_DOCS = [
    {
        "filename": "security_policy.txt",
        "title": "Security Policy",
        "text": (
            "Employees must use company-managed devices for production access. "
            "Access reviews are completed quarterly by department leads. "
            "Incident escalation must begin within 30 minutes for high-severity issues."
        ),
        "department": "IT",
        "version": "2.1",
        "document_type": "policy",
    },
    {
        "filename": "onboarding_playbook.txt",
        "title": "Onboarding Playbook",
        "text": (
            "Managers should complete role onboarding plans before a new hire start date. "
            "Access requests should be submitted at least three business days in advance. "
            "The first-week checklist includes equipment setup, payroll validation, and buddy assignment."
        ),
        "department": "People Ops",
        "version": "1.4",
        "document_type": "playbook",
    },
]


def seed_defaults() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(User).count() == 0:
            for item in DEFAULT_USERS:
                db.add(User(**item))
            db.commit()

        from app.db.models import Document

        if db.query(Document).count() == 0:
            admin = db.query(User).filter(User.role == "admin").first()
            if admin:
                service = IngestionService(db)
                for item in DEMO_DOCS:
                    service.ingest_text(
                        filename=item["filename"],
                        title=item["title"],
                        text=item["text"],
                        uploaded_by=admin,
                        department=item["department"],
                        version=item["version"],
                        document_type=item["document_type"],
                        approved=True,
                    )
                db.commit()
    finally:
        db.close()
