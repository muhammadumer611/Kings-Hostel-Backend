from app.firebase.firebase import db


class ComplaintRepository:
    def create_complaint(self, complaint_data: dict):
        complaint_ref = db.collection("complaints").document()
        complaint_ref.set(complaint_data)
        return complaint_ref.id

    def get_all_complaints(self):
        complaints = db.collection("complaints").stream()
        result = []
        for complaint in complaints:
            data = complaint.to_dict()
            data["firebase_id"] = complaint.id
            result.append(data)
        return result
