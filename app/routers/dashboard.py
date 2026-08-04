from fastapi import APIRouter

from app.schemas.dashboard import DashboardResponseSchema
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

dashboard_service = DashboardService()


@router.get(
    "/summary",
    response_model=DashboardResponseSchema,
    summary="Dashboard Summary",
    description="Returns complete dashboard statistics and recent records.",
)
def get_dashboard_summary():
    return dashboard_service.get_dashboard_summary()