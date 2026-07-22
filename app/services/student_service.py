from datetime import datetime
from app.repositories.student_repository import StudentRepository
from app.utils.student_id_generator import StudentIDGenerator


class StudentService:

    def __init__(self):
        self.repository = StudentRepository()
        self.id_generator = StudentIDGenerator()

    def _normalize_student_data(self, student_data: dict) -> dict:
        if "personal" in student_data and "guardian" in student_data and "allocation" in student_data:
            personal = student_data.get("personal") or {}
            guardian = student_data.get("guardian") or {}
            allocation = student_data.get("allocation") or {}

            return {
                "name": personal.get("name") or student_data.get("name") or student_data.get("full_name"),
                "cnic": personal.get("cnic") or student_data.get("cnic"),
                "phone": personal.get("phone") or student_data.get("phone"),
                "email": personal.get("email") or student_data.get("email"),
                "guardian_name": guardian.get("name") or student_data.get("guardian_name") or student_data.get("father_name"),
                "guardian_phone": guardian.get("phone") or student_data.get("guardian_phone"),
                "guardian_cnic": guardian.get("cnic") or student_data.get("guardian_cnic"),
                "block": allocation.get("block") or student_data.get("block"),
                "room_type": allocation.get("roomType") or student_data.get("room_type"),
                "blood_group": personal.get("bloodGroup") or student_data.get("blood_group"),
                "status": student_data.get("status", "Active"),
            }

        return {
            "name": student_data.get("name") or student_data.get("full_name"),
            "cnic": student_data.get("cnic"),
            "phone": student_data.get("phone"),
            "email": student_data.get("email"),
            "guardian_name": student_data.get("guardian_name") or student_data.get("father_name"),
            "guardian_phone": student_data.get("guardian_phone"),
            "guardian_cnic": student_data.get("guardian_cnic"),
            "block": student_data.get("block"),
            "room_type": student_data.get("room_type"),
            "blood_group": student_data.get("blood_group"),
            "status": student_data.get("status", "Active"),
        }

    def _serialize_student(self, student: dict) -> dict:
        created_at = student.get("created_at")
        join_date = None
        if isinstance(created_at, datetime):
            join_date = created_at.strftime("%Y-%m-%d")

        return {
            "id": student.get("student_id") or student.get("firebase_id"),
            "name": student.get("name") or student.get("full_name"),
            "cnic": student.get("cnic"),
            "rollNumber": student.get("student_id") or "",
            "email": student.get("email"),
            "phone": student.get("phone"),
            "block": student.get("block") or "",
            "roomNumber": student.get("room_number") or student.get("room") or "",
            "bedNumber": student.get("bed_number") or "",
            "guardianName": student.get("guardian_name") or student.get("father_name"),
            "guardianPhone": student.get("guardian_phone"),
            "guardianCnic": student.get("guardian_cnic"),
            "status": student.get("status", "Active"),
            "course": student.get("course") or "",
            "year": student.get("year") or "",
            "joinDate": join_date or "",
            "avatarUrl": student.get("avatar_url") or "",
            "cnicFrontUrl": student.get("cnic_front_url"),
            "cnicBackUrl": student.get("cnic_back_url"),
            "monthlyFee": student.get("monthly_fee", 0),
            "securityDeposit": student.get("security_deposit", 0),
            "pendingFee": student.get("pending_fee", 0),
            "feeStatus": student.get("fee_status", "Pending"),
            "emergencyContact": student.get("emergency_contact") or "",
            "permanentAddress": student.get("address") or "",
            "city": student.get("city") or "",
            "bloodGroup": student.get("blood_group") or "",
        }

    def create_student(self, student_data: dict):
        normalized_student = self._normalize_student_data(student_data)

        existing_student = self.repository.get_student_by_cnic(normalized_student.get("cnic", ""))
        if existing_student:
            return {
                "success": False,
                "message": "Student with this CNIC already exists.",
                "errors": None,
                "data": None,
            }

        existing_phone = self.repository.get_student_by_phone(normalized_student.get("phone", ""))
        if existing_phone:
            return {
                "success": False,
                "message": "Phone number already exists.",
                "errors": None,
                "data": None,
            }

        normalized_student["student_id"] = self.id_generator.generate()
        firebase_id = self.repository.create_student(normalized_student)

        return {
            "success": True,
            "message": "Student added successfully.",
            "data": {
                "student_id": normalized_student["student_id"],
                "firebase_id": firebase_id,
            },
            "errors": None,
        }

    def get_all_students(self):
        students = self.repository.get_all_students()
        serialized_students = [self._serialize_student(student) for student in students]

        return {
            "success": True,
            "message": "Students retrieved successfully.",
            "data": {
                "total_students": len(serialized_students),
                "students": serialized_students,
            },
            "errors": None,
        }

    def get_student_by_id(self, student_id: str):
        student = self.repository.get_student_by_id(student_id)
        if not student:
            return {
                "success": False,
                "message": "Student not found.",
                "data": None,
                "errors": None,
            }

        return {
            "success": True,
            "message": "Student retrieved successfully.",
            "data": self._serialize_student(student),
            "errors": None,
        }