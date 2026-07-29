from datetime import datetime, UTC

from app.firebase.firebase import db
from app.utils.logger import logger


class StudentRepository:

    def __init__(self):
        self.collection = db.collection("students")

    def _get_timestamp(self):
        return datetime.now(UTC).isoformat()

    def _normalize_student_data(self, student_data: dict) -> dict:
        normalized = dict(student_data or {})

        if "student_id" in normalized:
            normalized["student_id"] = str(normalized["student_id"]).strip().upper()

        if "name" in normalized:
            normalized["name"] = str(normalized["name"]).strip().title()

        if "cnic" in normalized:
            normalized["cnic"] = str(normalized["cnic"]).strip()

        if "phone" in normalized:
            normalized["phone"] = str(normalized["phone"]).strip()

        if "email" in normalized and normalized["email"]:
            normalized["email"] = str(normalized["email"]).strip().lower()

        if "blood_group" in normalized and normalized["blood_group"]:
            normalized["blood_group"] = str(normalized["blood_group"]).strip().upper()

        if "address" in normalized:
            normalized["address"] = str(normalized["address"]).strip()

        if "guardian_name" in normalized:
            normalized["guardian_name"] = str(normalized["guardian_name"]).strip().title()

        if "guardian_phone" in normalized:
            normalized["guardian_phone"] = str(normalized["guardian_phone"]).strip()

        if "guardian_cnic" in normalized:
            normalized["guardian_cnic"] = str(normalized["guardian_cnic"]).strip()

        if "relation" in normalized and normalized["relation"]:
            normalized["relation"] = str(normalized["relation"]).strip().title()

        if "room_firebase_id" in normalized and normalized["room_firebase_id"]:
            normalized["room_firebase_id"] = str(normalized["room_firebase_id"]).strip()

        if "room_number" in normalized and normalized["room_number"]:
            normalized["room_number"] = str(normalized["room_number"]).strip().upper()

        if "floor" in normalized and normalized["floor"] is not None:
            normalized["floor"] = int(normalized["floor"])

        if "bed_number" in normalized and normalized["bed_number"]:
            normalized["bed_number"] = str(normalized["bed_number"]).strip().upper()

        if "monthly_fee" in normalized and normalized["monthly_fee"] is not None:
            normalized["monthly_fee"] = float(normalized["monthly_fee"])

        if "security_deposit" in normalized and normalized["security_deposit"] is not None:
            normalized["security_deposit"] = float(normalized["security_deposit"])

        if "pending_fee" in normalized and normalized["pending_fee"] is not None:
            normalized["pending_fee"] = float(normalized["pending_fee"])

        return normalized

    def create_student(self, student_data: dict):
        try:
            student_data = self._normalize_student_data(student_data)

            student_data.setdefault("is_active", True)
            student_data.setdefault("pending_fee", 0.0)
            student_data.setdefault("fee_status", "Pending")
            student_data.setdefault("monthly_fee", 0.0)
            student_data.setdefault("security_deposit", 0.0)

            student_data.setdefault("room_firebase_id", None)
            student_data.setdefault("room_number", None)
            student_data.setdefault("floor", None)
            student_data.setdefault("bed_number", None)

            student_data["created_at"] = self._get_timestamp()
            student_data["updated_at"] = self._get_timestamp()

            student_ref = self.collection.document()

            student_ref.set(student_data)

            logger.info(
                f"Student created successfully | Firebase ID: {student_ref.id}"
            )

            return student_ref.id

        except Exception:
            logger.exception("Failed to create student.")
            raise

    def get_student_by_firebase_id(self, firebase_id: str):
        try:
            student = self.collection.document(firebase_id).get()

            if not student.exists:
                return None

            data = student.to_dict() or {}
            data["firebase_id"] = student.id

            logger.info(
                f"Student retrieved successfully | Firebase ID: {firebase_id}"
            )

            return data

        except Exception:
            logger.exception("Failed to retrieve student by Firebase ID.")
            raise

    def get_student_by_email(self, email: str):
        try:
            email = str(email).strip().lower()

            students = (
                self.collection
                .where("email", "==", email)
                .where("is_active", "==", True)
                .limit(1)
                .stream()
            )

            for student in students:
                data = student.to_dict() or {}
                data["firebase_id"] = student.id
                return data

            return None

        except Exception:
            logger.exception("Failed to retrieve student by email.")
            raise

    def get_student_by_student_id(self, student_id: str):
        try:
            student_id = str(student_id).strip().upper()

            students = (
                self.collection
                .where("student_id", "==", student_id)
                .where("is_active", "==", True)
                .limit(1)
                .stream()
            )

            for student in students:
                data = student.to_dict() or {}
                data["firebase_id"] = student.id
                return data

            return None

        except Exception:
            logger.exception("Failed to retrieve student by Student ID.")
            raise

    def get_student_by_cnic(self, cnic: str):
        try:
            cnic = str(cnic).strip()

            students = (
                self.collection
                .where("cnic", "==", cnic)
                .where("is_active", "==", True)
                .limit(1)
                .stream()
            )

            for student in students:
                data = student.to_dict() or {}
                data["firebase_id"] = student.id
                return data

            return None

        except Exception:
            logger.exception("Failed to retrieve student by CNIC.")
            raise

    def get_student_by_phone(self, phone: str):
        try:
            phone = str(phone).strip()

            students = (
                self.collection
                .where("phone", "==", phone)
                .where("is_active", "==", True)
                .limit(1)
                .stream()
            )

            for student in students:
                data = student.to_dict() or {}
                data["firebase_id"] = student.id
                return data

            return None

        except Exception:
            logger.exception("Failed to retrieve student by phone.")
            raise

    def get_all_students(self):
        try:
            students = (
                self.collection
                .where("is_active", "==", True)
                .stream()
            )

            student_list = []

            for student in students:
                data = student.to_dict()
                data["firebase_id"] = student.id
                student_list.append(data)

            student_list = sorted(
                student_list,
                key=lambda x: (
                    str(x.get("student_id", "")).upper(),
                    str(x.get("name", "")).upper(),
                ),
            )

            return student_list

        except Exception:
            logger.exception("Failed to fetch students")
            raise

    def student_exists(self, student_id: str):
        try:
            return self.get_student_by_student_id(student_id) is not None

        except Exception:
            logger.exception("Failed to check student existence.")
            raise

    def count_students(self):
        try:
            return sum(
                1
                for _ in self.collection
                .where("is_active", "==", True)
                .stream()
            )

        except Exception:
            logger.exception("Failed to count students")
            raise

    def update_student(
        self,
        student_id: str,
        student_data: dict,
    ):
        try:
            students = (
                self.collection
                .where("student_id", "==", student_id)
                .limit(1)
                .stream()
            )

            for student in students:
                student_data = self._normalize_student_data(student_data)
                student_data["updated_at"] = self._get_timestamp()

                self.collection.document(
                    student.id
                ).update(student_data)

                return True

            return False

        except Exception:
            logger.exception(
                "Failed to update student"
            )
            raise

    def delete_student(
        self,
        student_id: str,
    ):
        try:
            students = (
                self.collection
                .where("student_id", "==", student_id)
                .limit(1)
                .stream()
            )

            for student in students:
                self.collection.document(
                    student.id
                ).delete()

                return True

            return False

        except Exception:
            logger.exception(
                "Failed to delete student"
            )
            raise

    def search_students(self, keyword: str):
        try:
            keyword = keyword.lower()

            students = self.collection.stream()

            result = []

            for student in students:
                data = student.to_dict()

                name = str(
                    data.get("name", "")
                ).lower()

                cnic = str(
                    data.get("cnic", "")
                ).lower()

                phone = str(
                    data.get("phone", "")
                ).lower()

                if (
                    keyword in name
                    or keyword in cnic
                    or keyword in phone
                ):
                    data["firebase_id"] = student.id
                    result.append(data)

            return result

        except Exception:
            logger.exception("Failed to search students")
            raise