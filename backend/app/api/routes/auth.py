from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.schemas.auth import LoginRequest, SessionResponse, UserSummary

router = APIRouter()


@router.post("/login", response_model=SessionResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> SessionResponse:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    return SessionResponse(
        token=user.email,
        user=UserSummary.model_validate(user),
    )


@router.get("/me", response_model=UserSummary)
def me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UserSummary:
    return UserSummary.model_validate(user)
