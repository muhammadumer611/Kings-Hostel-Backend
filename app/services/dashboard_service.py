from app.repositories.dashboard_repository import DashboardRepository
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class DashboardService:

    def __init__(self):

        self.dashboard_repo = DashboardRepository()