from datetime import datetime

from app.repositories.student_repository import StudentRepository
from app.utils.student_id_generator import StudentIDGenerator
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class StudentService:

    def __init__(self):
        self.repository = StudentRepository()
        self.id_generator = StudentIDGenerator()

    def _normalize_student_data(self, student_data: dict) -> dict:

        if (
            "personal" in student_data
            and "guardian" in student_data
            and "allocation" in student_data
        ):

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

        existing_student = self.repository.get_student_by_cnic(
            normalized_student.get("cnic", "")
        )

        if existing_student:
            logger.warning(
                f"Duplicate CNIC detected: {normalized_student.get('cnic')}"
            )

            return APIResponse.error(
                "Student with this CNIC already exists."
            )

        existing_phone = self.repository.get_student_by_phone(
            normalized_student.get("phone", "")
        )

        if existing_phone:
            logger.warning(
                f"Duplicate Phone detected: {normalized_student.get('phone')}"
            )

            return APIResponse.error(
                "Phone number already exists."
            )

        normalized_student["student_id"] = self.id_generator.generate()

        try:

            firebase_id = self.repository.create_student(
                normalized_student
            )

            logger.info(
                f"Student created successfully | "
                f"Student ID: {normalized_student['student_id']} | "
                f"Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                "Student added successfully.",
                {
                    "student_id": normalized_student["student_id"],
                    "firebase_id": firebase_id,
                },
            )

        except Exception as e:

            logger.exception(
                f"Failed to create student | Error: {str(e)}"
            )

            return APIResponse.error(
                "Unable to create student.",
                str(e),
            )
    def get_all_students(self):

        try:

            students = self.repository.get_all_students()

            serialized_students = [
                self._serialize_student(student)
                for student in students
            ]

            logger.info(
                f"Students fetched successfully | Total Students: {len(serialized_students)}"
            )

            return APIResponse.success(
                "Students retrieved successfully.",
                {
                    "total_students": len(serialized_students),
                    "students": serialized_students,
                },
            )

        except Exception as e:

            logger.exception(
                f"Failed to fetch students | Error: {str(e)}"
            )

            return APIResponse.error(
                "Unable to fetch students.",
                str(e),
            )

    def get_student_by_id(self, student_id: str):

        try:

            student = self.repository.get_student_by_id(student_id)

            if not student:

                logger.warning(
                    f"Student not found | Student ID: {student_id}"
                )

                return APIResponse.error(
                    "Student not found."
                )

            logger.info(
                f"Student fetched successfully | Student ID: {student_id}"
            )

            return APIResponse.success(
                "Student retrieved successfully.",
                self._serialize_student(student),
            )

        except Exception as e:

            logger.exception(
                f"Failed to fetch student | Student ID: {student_id} | Error: {str(e)}"
            )

            return APIResponse.error(
                "Unable to fetch student.",
                str(e),
            )