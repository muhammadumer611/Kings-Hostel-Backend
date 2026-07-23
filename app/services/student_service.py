from datetime import datetime

from app.repositories.student_repository import StudentRepository
from app.utils.student_id_generator import StudentIDGenerator
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class StudentService:

    def __init__(self):

        self.repository = StudentRepository()
        self.id_generator = StudentIDGenerator()

    def _normalize_student_data(
        self,
        student_data: dict,
    ) -> dict:

        # ---------- New Frontend Payload ----------
        if (
            "personal" in student_data
            and "guardian" in student_data
            and "allocation" in student_data
        ):

            personal = student_data.get("personal") or {}
            guardian = student_data.get("guardian") or {}
            allocation = student_data.get("allocation") or {}

            return {
                "name": personal.get("name"),
                "cnic": personal.get("cnic"),
                "phone": personal.get("phone"),
                "email": personal.get("email"),
                "blood_group": personal.get("bloodGroup"),

                "guardian_name": guardian.get("name"),
                "guardian_phone": guardian.get("phone"),
                "guardian_cnic": guardian.get("cnic"),

                "block": allocation.get("block"),
                "room_type": allocation.get("roomType"),

                "room_number": allocation.get("roomNumber"),
                "bed_number": allocation.get("bedNumber"),

                "status": student_data.get(
                    "status",
                    "Active",
                ),
            }

        # ---------- Legacy Payload ----------
        return {"name": (student_data.get("name")
            or student_data.get("full_name")),
            "cnic": student_data.get("cnic"),
            "phone": student_data.get("phone"),
            "email":student_data.get("email"),
            "blood_group": student_data.get("blood_group"),
            "guardian_name": (student_data.get("guardian_name")
                or student_data.get("father_name")),
            "guardian_phone": student_data.get("guardian_phone"),
            "guardian_cnic": student_data.get("guardian_cnic"),
            "block": student_data.get("block"),
            "room_type": student_data.get("room_type"),
            "room_number": student_data.get("room_number"),
            "bed_number": student_data.get("bed_number"),
            "status": student_data.get("status","Active"),
        }

    def _serialize_student(
        self,
        student: dict,
    ) -> dict:
        """
        Convert database document into
        frontend response format.
        """

        created_at = student.get("created_at")

        join_date = ""

        if isinstance(created_at, datetime):
            join_date = created_at.strftime("%Y-%m-%d")

        return {
            "id": (
                student.get("student_id")
                or student.get("firebase_id")
            ),
            "studentId": student.get("student_id", ""),
            "name": student.get("name", ""),
            "cnic": student.get("cnic", ""),
            "email": student.get("email", ""),
            "phone": student.get("phone", ""),
            "block": student.get("block", ""),
            "roomType": student.get("room_type", ""),
            "roomNumber": student.get("room_number", ""),
            "bedNumber": student.get("bed_number", ""),
            "guardianName": student.get("guardian_name", ""),
            "guardianPhone": student.get("guardian_phone", ""),
            "guardianCnic": student.get("guardian_cnic", ""),
            "bloodGroup": student.get("blood_group", ""),
            "status": student.get("status", "Active"),
            "course": student.get("course", ""),
            "year": student.get("year", ""),
            "monthlyFee": student.get("monthly_fee", 0),
            "securityDeposit": student.get("security_deposit", 0),
            "pendingFee": student.get("pending_fee", 0),
            "feeStatus": student.get("fee_status", "Pending"),
            "avatarUrl": student.get("avatar_url", ""),
            "cnicFrontUrl": student.get("cnic_front_url", ""),
            "cnicBackUrl": student.get("cnic_back_url", ""),
            "emergencyContact": student.get("emergency_contact", ""),
            "permanentAddress": student.get("address", ""),
            "city": student.get("city", ""),
            "joinDate": join_date,
        }

    def create_student(
        self,
        student_data: dict,
    ):

        try:

            normalized_student = self._normalize_student_data(
                student_data
            )

            existing_student = (
                self.repository.get_student_by_cnic(
                    normalized_student.get("cnic", "")
                )
            )

            if existing_student:

                logger.warning(
                    "Duplicate CNIC detected | "
                    f"CNIC: {normalized_student.get('cnic')}"
                )

                return APIResponse.error(
                    "Student with this CNIC already exists."
                )

            existing_phone = (
                self.repository.get_student_by_phone(
                    normalized_student.get("phone", "")
                )
            )

            if existing_phone:

                logger.warning(
                    "Duplicate phone detected | "
                    f"Phone: {normalized_student.get('phone')}"
                )

                return APIResponse.error(
                    "Phone number already exists."
                )

            normalized_student["student_id"] = (
                self.id_generator.generate()
            )

            firebase_id = self.repository.create_student(
                normalized_student
            )

            logger.info(
                "Student created successfully | "
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
                "Failed to create student."
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
                "Students retrieved successfully | "
                f"Total Students: {len(serialized_students)}"
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
                "Failed to retrieve students."
            )

            return APIResponse.error(
                "Unable to retrieve students.",
                str(e),
            )

    def get_student_by_id(
        self,
        student_id: str,
    ):

        try:

            student = self.repository.get_student_by_id(
                student_id
            )

            if not student:

                logger.warning(
                    "Student not found | "
                    f"Student ID: {student_id}"
                )

                return APIResponse.error(
                    "Student not found."
                )

            serialized_student = self._serialize_student(
                student
            )

            logger.info(
                "Student retrieved successfully | "
                f"Student ID: {student_id}"
            )

            return APIResponse.success(
                "Student retrieved successfully.",
                serialized_student,
            )

        except Exception as e:

            logger.exception(
                "Failed to retrieve student."
            )

            return APIResponse.error(
                "Unable to retrieve student.",
                str(e),
            )

    def update_student(
        self,
        student_id: str,
        student_data: dict,
    ):

        try:

            student = self.repository.get_student_by_id(
                student_id
            )

            if not student:

                logger.warning(
                    "Student not found for update | "
                    f"Student ID: {student_id}"
                )

                return APIResponse.error(
                    "Student not found."
                )

            update_data = {}

            if "personal" in student_data:

                personal = student_data["personal"]

                if "name" in personal:
                    update_data["name"] = personal["name"]

                if "cnic" in personal:
                    update_data["cnic"] = personal["cnic"]

                if "phone" in personal:
                    update_data["phone"] = personal["phone"]

                if "email" in personal:
                    update_data["email"] = personal["email"]

                if "bloodGroup" in personal:
                    update_data["blood_group"] = personal["bloodGroup"]

            if "guardian" in student_data:

                guardian = student_data["guardian"]

                if "name" in guardian:
                    update_data["guardian_name"] = guardian["name"]

                if "phone" in guardian:
                    update_data["guardian_phone"] = guardian["phone"]

                if "cnic" in guardian:
                    update_data["guardian_cnic"] = guardian["cnic"]

            if "allocation" in student_data:

                allocation = student_data["allocation"]

                if "block" in allocation:
                    update_data["block"] = allocation["block"]

                if "roomType" in allocation:
                    update_data["room_type"] = allocation["roomType"]

                if "roomNumber" in allocation:
                    update_data["room_number"] = allocation["roomNumber"]

                if "bedNumber" in allocation:
                    update_data["bed_number"] = allocation["bedNumber"]

            if "status" in student_data:
                update_data["status"] = student_data["status"]

            if (
                "cnic" in update_data
                and update_data["cnic"] != student.get("cnic")
            ):

                existing_student = self.repository.get_student_by_cnic(
                    update_data["cnic"]
                )

                if existing_student:

                    logger.warning(
                        "Duplicate CNIC detected during update | "
                        f"CNIC: {update_data['cnic']}"
                    )

                    return APIResponse.error(
                        "Student with this CNIC already exists."
                    )

            if (
                "phone" in update_data
                and update_data["phone"] != student.get("phone")
            ):

                existing_phone = self.repository.get_student_by_phone(
                    update_data["phone"]
                )

                if existing_phone:

                    logger.warning(
                        "Duplicate phone detected during update | "
                        f"Phone: {update_data['phone']}"
                    )

                    return APIResponse.error(
                        "Phone number already exists."
                    )

            self.repository.update_student(
                student_id,
                update_data,
            )

            updated_student = self.repository.get_student_by_id(
                student_id
            )

            logger.info(
                "Student updated successfully | "
                f"Student ID: {student_id}"
            )

            return APIResponse.success(
                "Student updated successfully.",
                self._serialize_student(updated_student),
            )

        except Exception as e:

            logger.exception(
                "Failed to update student."
            )

            return APIResponse.error(
                "Unable to update student.",
                str(e),
            )

    def delete_student(
        self,
        student_id: str,
    ):

        try:

            if not self.repository.student_exists(
                student_id
            ):

                logger.warning(
                    "Student not found for deletion | "
                    f"Student ID: {student_id}"
                )

                return APIResponse.error(
                    "Student not found."
                )

            self.repository.delete_student(
                student_id
            )

            logger.info(
                "Student deleted successfully | "
                f"Student ID: {student_id}"
            )

            return APIResponse.success(
                "Student deleted successfully."
            )

        except Exception as e:

            logger.exception(
                "Failed to delete student."
            )

            return APIResponse.error(
                "Unable to delete student.",
                str(e),
            )

    def search_students(
        self,
        keyword: str,
    ):

        try:

            keyword = keyword.strip()

            if not keyword:

                return APIResponse.error(
                    "Search keyword is required."
                )

            students = self.repository.search_students(
                keyword
            )

            serialized_students = [
                self._serialize_student(student)
                for student in students
            ]

            logger.info(
                "Student search completed | "
                f"Keyword: {keyword} | "
                f"Results: {len(serialized_students)}"
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
                "Failed to search students."
            )

            return APIResponse.error(
                "Unable to search students.",
                str(e),
            )

    def count_students(self):

        try:

            total_students = self.repository.count_students()

            logger.info(
                "Student count retrieved successfully | "
                f"Total Students: {total_students}"
            )

            return APIResponse.success(
                "Student count retrieved successfully.",
                {
                    "total_students": total_students,
                },
            )

        except Exception as e:

            logger.exception(
                "Failed to count students."
            )

            return APIResponse.error(
                "Unable to count students.",
                str(e),
            )