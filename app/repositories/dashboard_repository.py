from app.firebase.firebase import db


class DashboardRepository:
    def get_students(self):
        students = db.collection("students").stream()
        return [student.to_dict() for student in students]

    def get_rooms(self):
        rooms = db.collection("rooms").stream()
        return [room.to_dict() for room in rooms]

    def get_fee_records(self):
        fees = db.collection("fees").stream()
        return [fee.to_dict() for fee in fees]

    def get_complaints(self):
        complaints = db.collection("complaints").stream()
        return [complaint.to_dict() for complaint in complaints]

    def get_activity_logs(self):
        logs = db.collection("activity_logs").stream()
        return [log.to_dict() for log in logs]
