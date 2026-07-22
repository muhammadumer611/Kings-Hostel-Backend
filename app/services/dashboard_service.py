from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(self):
        self.repository = DashboardRepository()

    def get_dashboard_summary(self):
        students = self.repository.get_students()
        rooms = self.repository.get_rooms()
        fee_records = self.repository.get_fee_records()
        complaints = self.repository.get_complaints()
        activity_logs = self.repository.get_activity_logs()

        total_students = len(students)
        active_students = sum(1 for student in students if student.get("status") == "Active")
        occupied_rooms = sum(
            1 for room in rooms if (room.get("occupied_beds") if "occupied_beds" in room else room.get("occupiedBeds", 0)) > 0
        )
        total_rooms = len(rooms)
        available_beds = sum(
            max(0, (room.get("total_beds") if "total_beds" in room else room.get("totalBeds", 0)) - (room.get("occupied_beds") if "occupied_beds" in room else room.get("occupiedBeds", 0))) for room in rooms
        )
        monthly_revenue = sum(float(fee.get("amount", 0) or 0) for fee in fee_records if fee.get("status") == "Paid")
        pending_fees_total = sum(float(fee.get("amount", 0) or 0) for fee in fee_records if fee.get("status") in {"Pending", "Partial", "Overdue"})
        active_complaints_count = sum(1 for complaint in complaints if complaint.get("status") != "Resolved")
        occupancy_rate = round((occupied_rooms / total_rooms * 100) if total_rooms else 0, 1)

        return {
            "success": True,
            "message": "Dashboard summary retrieved successfully.",
            "data": {
                "stats": {
                    "totalStudents": total_students,
                    "activeStudents": active_students,
                    "occupancyRate": occupancy_rate,
                    "monthlyRevenue": int(monthly_revenue),
                    "pendingFeesTotal": int(pending_fees_total),
                    "securityDepositTotal": 0,
                    "activeComplaintsCount": active_complaints_count,
                    "totalRooms": total_rooms,
                    "occupiedRooms": occupied_rooms,
                    "availableBeds": available_beds,
                },
                "recentAdmissions": students[:5],
                "recentPayments": fee_records[:5],
                "activityLogs": activity_logs[:5],
                "complaints": complaints[:5],
            },
            "errors": None,
        }
