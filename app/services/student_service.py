from app.repositories.student_repository import StudentRepository
from app.utils.student_id_generator import StudentIDGenerator
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class StudentService:

    def __init__(self):
        self.repository = StudentRepository()
        self.id_generator = StudentIDGenerator()

    def _normalize_student_data(self, student_data: dict) -> dict:

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
                "blood_group": personal.get("blood_group") or personal.get("bloodGroup"),
                "profile_image": personal.get("profile_image") or personal.get("profileImage"),
                "cnic_front_image": personal.get("cnic_front_image") or personal.get("cnicFrontImage"),
                "cnic_back_image": personal.get("cnic_back_image") or personal.get("cnicBackImage"),

                "guardian_name": guardian.get("guardian_name") or guardian.get("name"),
                "guardian_phone": guardian.get("guardian_phone") or guardian.get("phone"),
                "guardian_cnic": guardian.get("guardian_cnic") or guardian.get("cnic"),
                "address": personal.get("address"),
                "relation": guardian.get("relation"),

                "block": allocation.get("block"),
                "room_type": allocation.get("room_type") or allocation.get("roomType"),
                "room_firebase_id": allocation.get("room_firebase_id") or allocation.get("roomFirebaseId"),
                "floor": allocation.get("floor"),
                "joining_date": allocation.get("joining_date") or allocation.get("joiningDate"),
                "remarks": allocation.get("remarks"),

                "room_number": allocation.get("room_number") or allocation.get("roomNumber"),
                "bed_number": allocation.get("bed_number") or allocation.get("bedNumber"),

                "monthly_fee": allocation.get("monthly_fee") or allocation.get("monthlyFee"),
                "security_deposit": allocation.get("security_deposit") or allocation.get("securityDeposit"),

                "status": student_data.get("status", "Active"),
            }

        # ---------- Legacy Payload ----------
        return {
            "name": student_data.get("name") or student_data.get("full_name"),
            "cnic": student_data.get("cnic"),
            "phone": student_data.get("phone"),
            "email": student_data.get("email"),
            "blood_group": student_data.get("blood_group"),
            "address": student_data.get("address"),
            "profile_image": student_data.get("profile_image"),
            "cnic_front_image": student_data.get("cnic_front_image"),
            "cnic_back_image": student_data.get("cnic_back_image"),
            "guardian_name": (
                student_data.get("guardian_name")
                or student_data.get("father_name")
            ),
            "relation": student_data.get("relation"),
            "guardian_phone": student_data.get("guardian_phone"),
            "guardian_cnic": student_data.get("guardian_cnic"),
            "block": student_data.get("block"),
            "room_type": student_data.get("room_type"),
            "room_number": student_data.get("room_number"),
            "bed_number": student_data.get("bed_number"),
            "room_firebase_id": student_data.get("room_firebase_id"),
            "floor": student_data.get("floor"),

            "joining_date": student_data.get("joining_date"),
            "remarks": student_data.get("remarks"),

            "monthly_fee": student_data.get("monthly_fee"),
            "security_deposit": student_data.get("security_deposit"),
            "status": student_data.get("status", "Active"),
        }

    def _serialize_student(self, student: dict) -> dict:
        created_at = student.get("created_at")
        updated_at = student.get("updated_at")

        return {
            "student_id": student.get("student_id", ""),
            "firebase_id": student.get("firebase_id", ""),

            "name": student.get("name", ""),
            "cnic": student.get("cnic", ""),
            "phone": student.get("phone", ""),
            "email": student.get("email", ""),
            "address": student.get("address"),
            "profile_image": student.get("profile_image"),
            "cnic_front_image": student.get("cnic_front_image"),
            "cnic_back_image": student.get("cnic_back_image"),

            "guardian_name": student.get("guardian_name"),
            "guardian_phone": student.get("guardian_phone"),
            "guardian_cnic": student.get("guardian_cnic"),
            "relation": student.get("relation"),

            "block": student.get("block"),
            "room_type": student.get("room_type"),
            "room_firebase_id": student.get("room_firebase_id"),
            "floor": student.get("floor"),

            "blood_group": student.get("blood_group"),
            "joining_date": student.get("joining_date"),
            "status": (
                        student.get("status").value
                        if hasattr(student.get("status"), "value")
                        else student.get("status", "Active")
                    ),
            "remarks": student.get("remarks"),

            "room_number": student.get("room_number"),
            "bed_number": student.get("bed_number"),

            "monthly_fee": student.get("monthly_fee", 0),
            "security_deposit": student.get("security_deposit", 0),
            "pending_fee": student.get("pending_fee", 0),
            "fee_status": student.get("fee_status", "Pending"),

            "created_at": (
                created_at.isoformat()
                if hasattr(created_at, "isoformat")
                else created_at
            ),

            "updated_at": (
                updated_at.isoformat()
                if hasattr(updated_at, "isoformat")
                else updated_at
            ),
        }

    def create_student(self, student_data: dict):
        try:
            normalized_student = self._normalize_student_data(student_data)

            print(student_data)
            print(normalized_student)

            if not normalized_student.get("name"):
                return APIResponse.error("Student name is required.")

            if not normalized_student.get("cnic"):
                return APIResponse.error("CNIC is required.")

            existing_student = self.repository.get_student_by_cnic(
                normalized_student.get("cnic", "")
            )

            if existing_student:
                logger.warning(
                    "Duplicate CNIC detected | "
                    f"CNIC: {normalized_student.get('cnic')}"
                )

                return APIResponse.error(
                    "Student with this CNIC already exists."
                )

            if not normalized_student.get("phone"):
                return APIResponse.error("Phone number is required.")

            existing_phone = self.repository.get_student_by_phone(
                normalized_student.get("phone", "")
            )

            if existing_phone:
                logger.warning(
                    "Duplicate phone detected | "
                    f"Phone: {normalized_student.get('phone')}"
                )

                return APIResponse.error(
                    "Phone number already exists."
                )

            if not normalized_student.get("guardian_name"):
                return APIResponse.error(
                    "Guardian name is required."
                )

            if not normalized_student.get("guardian_phone"):
                return APIResponse.error(
                    "Guardian phone is required."
                )

            if not normalized_student.get("guardian_cnic"):
                return APIResponse.error(
                    "Guardian CNIC is required."
                )

            if not normalized_student.get("address"):
                return APIResponse.error(
                    "Address is required."
                )

            email = (normalized_student.get("email") or "").strip()

            if email:
                existing_email = self.repository.get_student_by_email(email)

                if existing_email:
                    return APIResponse.error(
                        "Email already exists."
                    )

            normalized_student["student_id"] = self.id_generator.generate()

            while self.repository.student_exists(normalized_student["student_id"]):
                normalized_student["student_id"] = self.id_generator.generate()

            firebase_id = self.repository.create_student(normalized_student)

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
            logger.exception("Failed to create student.")

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
            logger.exception("Failed to retrieve students.")

            return APIResponse.error(
                "Unable to retrieve students.",
                str(e),
            )

    def get_student_by_id(self, student_id: str):
        try:
            student_id = str(student_id).strip().upper()

            student = self.repository.get_student_by_student_id(student_id)

            if not student:
                logger.warning(
                    "Student not found | "
                    f"Student ID: {student_id}"
                )

                return APIResponse.error(
                    "Student not found."
                )

            serialized_student = self._serialize_student(student)

            logger.info(
                "Student retrieved successfully | "
                f"Student ID: {student_id}"
            )

            return APIResponse.success(
                "Student retrieved successfully.",
                serialized_student,
            )

        except Exception as e:
            logger.exception("Failed to retrieve student.")

            return APIResponse.error(
                "Unable to retrieve student.",
                str(e),
            )

    def update_student(self, student_id: str, student_data: dict):
        try:
            student_id = str(student_id).strip().upper()
            student = self.repository.get_student_by_student_id(student_id)

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
                personal = student_data["personal"] or {}

                if "name" in personal:
                    update_data["name"] = personal["name"]

                if "cnic" in personal:
                    update_data["cnic"] = personal["cnic"]

                if "phone" in personal:
                    update_data["phone"] = personal["phone"]

                if "email" in personal:
                    update_data["email"] = personal["email"]

                if "blood_group" in personal or "bloodGroup" in personal:
                    update_data["blood_group"] = (
                        personal.get("blood_group") or personal.get("bloodGroup")
                    )

                if "address" in personal:
                    update_data["address"] = personal["address"]

                if "profile_image" in personal or "profileImage" in personal:
                    update_data["profile_image"] = (
                        personal.get("profile_image") or personal.get("profileImage")
                    )

                if "cnic_front_image" in personal or "cnicFrontImage" in personal:
                    update_data["cnic_front_image"] = (
                        personal.get("cnic_front_image") or personal.get("cnicFrontImage")
                    )

                if "cnic_back_image" in personal or "cnicBackImage" in personal:
                    update_data["cnic_back_image"] = (
                        personal.get("cnic_back_image") or personal.get("cnicBackImage")
                    )

            if "guardian" in student_data:
                guardian = student_data["guardian"] or {}

                if "guardian_name" in guardian or "name" in guardian:
                    update_data["guardian_name"] = (
                        guardian.get("guardian_name") or guardian.get("name")
                    )

                if "guardian_phone" in guardian or "phone" in guardian:
                    update_data["guardian_phone"] = (
                        guardian.get("guardian_phone") or guardian.get("phone")
                    )

                if "guardian_cnic" in guardian or "cnic" in guardian:
                    update_data["guardian_cnic"] = (
                        guardian.get("guardian_cnic") or guardian.get("cnic")
                    )

                if "relation" in guardian:
                    update_data["relation"] = guardian["relation"]

            if "allocation" in student_data:
                allocation = student_data["allocation"] or {}

                if "block" in allocation:
                    update_data["block"] = allocation["block"]

                if "room_type" in allocation or "roomType" in allocation:
                    update_data["room_type"] = (
                        allocation.get("room_type") or allocation.get("roomType")
                    )

                if "room_number" in allocation or "roomNumber" in allocation:
                    update_data["room_number"] = (
                        allocation.get("room_number") or allocation.get("roomNumber")
                    )

                if "bed_number" in allocation or "bedNumber" in allocation:
                    update_data["bed_number"] = (
                        allocation.get("bed_number") or allocation.get("bedNumber")
                    )

                if "room_firebase_id" in allocation or "roomFirebaseId" in allocation:
                    update_data["room_firebase_id"] = (
                        allocation.get("room_firebase_id") or allocation.get("roomFirebaseId")
                    )

                if "floor" in allocation:
                    update_data["floor"] = allocation["floor"]

                if "joining_date" in allocation or "joiningDate" in allocation:
                    update_data["joining_date"] = (
                        allocation.get("joining_date") or allocation.get("joiningDate")
                    )

                if "remarks" in allocation:
                    update_data["remarks"] = allocation["remarks"]

                if "monthly_fee" in allocation or "monthlyFee" in allocation:
                    update_data["monthly_fee"] = (
                        allocation.get("monthly_fee") or allocation.get("monthlyFee")
                    )

                if "security_deposit" in allocation or "securityDeposit" in allocation:
                    update_data["security_deposit"] = (
                        allocation.get("security_deposit") or allocation.get("securityDeposit")
                    )

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
                    return APIResponse.error(
                        "Phone number already exists."
                    )

            if (
                update_data.get("email")
                and update_data["email"] != student.get("email")
            ):
                existing_email = self.repository.get_student_by_email(
                    update_data["email"]
                )

                if existing_email:
                    return APIResponse.error(
                        "Email already exists."
                    )

            if not update_data:
                return APIResponse.error(
                    "No data provided for update."
                )

            updated = self.repository.update_student(student_id, update_data)

            if not updated:
                return APIResponse.error(
                    "Student update failed."
                )

            updated_student = self.repository.get_student_by_student_id(student_id)

            if not updated_student:
                return APIResponse.error(
                    "Student not found after update."
                )

            serialized_student = self._serialize_student(updated_student)

            logger.info(
                "Student updated successfully | "
                f"Student ID: {student_id}"
            )

            return APIResponse.success(
                "Student updated successfully.",
                serialized_student,
            )

        except Exception as e:
            logger.exception("Failed to update student.")

            return APIResponse.error(
                "Unable to update student.",
                str(e),
            )

    def delete_student(self, student_id: str):
        try:
            student_id = str(student_id).strip().upper()

            if not self.repository.student_exists(student_id):
                logger.warning(
                    "Student not found for deletion | "
                    f"Student ID: {student_id}"
                )

                return APIResponse.error(
                    "Student not found."
                )

            deleted = self.repository.disable_student(student_id)

            if not deleted:
                return APIResponse.error("Student not found.")

            logger.info(
                "Student disabled successfully | "
                f"Student ID: {student_id}"
            )

            return APIResponse.success(
                "Student disabled successfully."
            )

        except Exception as e:
            logger.exception("Failed to disable student.")

            return APIResponse.error(
                "Unable to disable student.",
                str(e),
            )

    def search_students(self, keyword: str):
        try:
            keyword = str(keyword).strip()

            if not keyword:
                return APIResponse.error(
                    "Search keyword is required."
                )

            students = self.repository.search_students(keyword)

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
            logger.exception("Failed to search students.")

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
            logger.exception("Failed to count students.")

            return APIResponse.error(
                "Unable to count students.",
                str(e),
            )