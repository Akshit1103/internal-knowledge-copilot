from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.db.models import User
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview", response_model=AnalyticsResponse)
def analytics_overview(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AnalyticsResponse:
    require_role(user, "admin")
    return AnalyticsService(db).build_overview()
