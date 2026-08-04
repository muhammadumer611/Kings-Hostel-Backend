from app.firebase.firebase import db

from app.repositories.student_repository import StudentRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.fee_repository import FeeRepository

from app.utils.logger import logger


class DashboardRepository:

    def __init__(self):

        self.student_repo = StudentRepository()
        self.room_repo = RoomRepository()
        self.fee_repo = FeeRepository()

        self.activity_collection = db.collection("activity_logs")

    # ==========================
    # Statistics
    # ==========================

    def get_student_statistics(self):
        return self.student_repo.get_student_statistics()

    def get_room_statistics(self):
        return self.room_repo.get_room_statistics()

    def get_fee_statistics(self):
        return self.fee_repo.get_fee_statistics()

   

    # ==========================
    # Recent Data
    # ==========================

    def get_recent_students(self, limit=5):

        students = self.student_repo.get_all_students()

        return students[:limit]

    def get_recent_fee_records(self, limit=5):

        fees = self.fee_repo.get_all_fee_records()

        return fees[:limit]

   

    # ==========================
    # Extra Dashboard Widgets
    # ==========================

    def get_available_rooms(self):

        return self.room_repo.get_available_rooms()

    def get_pending_fee_records(self):

        return self.fee_repo.get_pending_fee_records()

    def get_overdue_fee_records(self):

        return self.fee_repo.get_overdue_fee_records()

    # ==========================
    # Activity Logs
    # ==========================

    def get_recent_activity_logs(self, limit=10):

        try:

            logs = (
                self.activity_collection
                .order_by("created_at", direction="DESCENDING")
                .limit(limit)
                .stream()
            )

            result = []

            for log in logs:

                data = log.to_dict() or {}

                data["firebase_id"] = log.id

                result.append(data)

            return result

        except Exception:

            logger.exception(
                "Failed to fetch activity logs."
            )

            return []