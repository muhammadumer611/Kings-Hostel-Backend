from app.repositories.complaint_repository import ComplaintRepository


class ComplaintService:
    def __init__(self):
        self.repository = ComplaintRepository()

    def create_complaint(self, complaint_data: dict):
        firebase_id = self.repository.create_complaint(complaint_data)
        return {
            "success": True,
            "message": "Complaint created successfully.",
            "data": {"firebase_id": firebase_id},
            "errors": None,
        }

    def get_all_complaints(self):
        complaints = self.repository.get_all_complaints()
        return {
            "success": True,
            "message": "Complaints retrieved successfully.",
            "data": {"complaints": complaints},
            "errors": None,
        }
