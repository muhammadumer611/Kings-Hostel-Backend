from app.repositories.student_repository import StudentRepository
from app.services.student_service import StudentService


class DummyRepository:
    def __init__(self):
        self.created = []
        self.cnic_values = []
        self.phone_values = []

    def get_student_by_cnic(self, cnic):
        self.cnic_values.append(cnic)
        return None

    def get_student_by_phone(self, phone):
        self.phone_values.append(phone)
        return None

    def create_student(self, student_data):
        self.created.append(student_data)
        return "firebase-id"


def test_repository_exposes_list_method():
    repository = StudentRepository()

    assert hasattr(repository, "get_all_students")
    assert callable(repository.get_all_students)


def test_create_student_success(monkeypatch):
    service = StudentService()
    service.repository = DummyRepository()

    result = service.create_student(
        {
            "full_name": "Ali Khan",
            "father_name": "Khan",
            "phone": "03001234567",
            "guardian_phone": "03007654321",
            "email": "student@example.com",
            "cnic": "35202-1234567-8",
            "address": "Lahore",
            "monthly_fee": 1000.0,
            "security_fee": 500.0,
            "status": "Active",
        }
    )

    assert result["success"] is True
    assert result["message"] == "Student added successfully."
    assert result["data"]["student_id"].startswith("STU")
    assert result["data"]["firebase_id"] == "firebase-id"
