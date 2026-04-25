from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not x_user_email:
        raise HTTPException(status_code=401, detail="Missing X-User-Email header.")

    user = db.query(User).filter(User.email == x_user_email.lower()).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user.")
    return user


def require_role(user: User, *roles: str) -> User:
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions.")
    return user
