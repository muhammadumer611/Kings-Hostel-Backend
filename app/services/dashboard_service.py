from app.repositories.dashboard_repository import DashboardRepository
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class DashboardService:

    def __init__(self):
        self.dashboard_repo = DashboardRepository()

    def get_dashboard_summary(self):
        try:

            student_stats = self.dashboard_repo.get_student_statistics()

            room_stats = self.dashboard_repo.get_room_statistics()

            fee_stats = self.dashboard_repo.get_fee_statistics()


            recent_students = self.dashboard_repo.get_recent_students()

            recent_fee_records = self.dashboard_repo.get_recent_fee_records()


            recent_activity_logs = self.dashboard_repo.get_recent_activity_logs()

            available_rooms = self.dashboard_repo.get_available_rooms()

            pending_fee_records = self.dashboard_repo.get_pending_fee_records()

            overdue_fee_records = self.dashboard_repo.get_overdue_fee_records()

           

            dashboard_data = {
                         "overview": {
                         "students": student_stats,
                         "rooms": room_stats,
                         "fees": fee_stats,
                     },

                "recent_students": recent_students,
                "recent_fee_records": recent_fee_records,
                "recent_activity_logs": recent_activity_logs,
                "available_rooms": available_rooms,
                "pending_fee_records": pending_fee_records,
                 "overdue_fee_records": overdue_fee_records,
            }

            logger.info("Dashboard summary generated successfully.")

            return APIResponse.success(
                message="Dashboard summary retrieved successfully.",
                data=dashboard_data,
            )

        except Exception:
            logger.exception("Failed to generate dashboard summary.")

            return APIResponse.error(
                message="Failed to generate dashboard summary."
            )