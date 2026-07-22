from app.services.dashboard_service import DashboardService


class DummyDashboardRepository:
    def get_students(self):
        return [{"status": "Active"}, {"status": "On Leave"}, {"status": "Vacated"}]

    def get_rooms(self):
        return [
            {"status": "Available", "totalBeds": 2, "occupiedBeds": 1},
            {"status": "Full", "totalBeds": 2, "occupiedBeds": 2},
        ]

    def get_fee_records(self):
        return [
            {"status": "Paid", "amount": 1000},
            {"status": "Pending", "amount": 500},
            {"status": "Partial", "amount": 300},
        ]

    def get_complaints(self):
        return [{"status": "Pending"}, {"status": "Resolved"}]

    def get_activity_logs(self):
        return [{"id": "1"}, {"id": "2"}]


def test_dashboard_summary_uses_frontend_contract():
    service = DashboardService()
    service.repository = DummyDashboardRepository()

    result = service.get_dashboard_summary()

    assert result["success"] is True
    assert result["data"]["stats"]["totalStudents"] == 3
    assert result["data"]["stats"]["activeComplaintsCount"] == 1
    assert result["data"]["stats"]["occupiedRooms"] == 2
    assert result["data"]["stats"]["availableBeds"] == 1
    assert len(result["data"]["activityLogs"]) == 2
