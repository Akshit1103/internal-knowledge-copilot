import json

from sqlalchemy.orm import Session

from app.db.models import AuditLog, User


def write_audit_log(
    db: Session,
    *,
    actor: User,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict,
) -> None:
    log = AuditLog(
        actor_email=actor.email,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details),
    )
    db.add(log)
