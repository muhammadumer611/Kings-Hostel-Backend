from datetime import datetime, UTC

from app.firebase.firebase import db
from app.routers import student
from app.utils.logger import logger


class StudentRepository:

    def __init__(self):
        self.collection = db.collection("students")

    def _student_query(self):
        return self.collection.where("is_active", "==", True)

    def _student_to_dict(self, student):
        data = student.to_dict() or {}
        data["firebase_id"] = student.id
        return data

    def _sort_students(self, students: list[dict]):
        students.sort(
            key=lambda x: (
                str(x.get("student_id", "")).upper(),
                str(x.get("name", "")).upper(),
            )
        )
        return students

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

        if "status" in normalized and normalized["status"]:
            normalized["status"] = str(normalized["status"]).strip().title()

        if "remarks" in normalized and normalized["remarks"]:
            normalized["remarks"] = str(normalized["remarks"]).strip()

        if "joining_date" in normalized and normalized["joining_date"]:
            normalized["joining_date"] = str(normalized["joining_date"]).strip()

        if "block" in normalized and normalized["block"]:
            normalized["block"] = str(normalized["block"]).strip().upper()

        if "room_type" in normalized and normalized["room_type"]:
            normalized["room_type"] = str(normalized["room_type"]).strip().title()

        if "fee_status" in normalized and normalized["fee_status"]:
            normalized["fee_status"] = str(normalized["fee_status"]).strip().title()

        return normalized

    def _prepare_student_data(self, student_data: dict) -> dict:
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

        timestamp = self._get_timestamp()

        student_data["created_at"] = timestamp
        student_data["updated_at"] = timestamp

        return student_data

    def _prepare_update_data(self, student_data: dict) -> dict:
        student_data = self._normalize_student_data(student_data)

        student_data.pop("student_id", None)
        student_data.pop("created_at", None)
        student_data.pop("firebase_id", None)

        student_data["updated_at"] = self._get_timestamp()

        return student_data

    def create_student(self, student_data: dict):
        try:
            student_data = self._prepare_student_data(student_data)

            student_ref = self.collection.document()

            student_ref.set(student_data)

            logger.info(f"Student created successfully | Firebase ID: {student_ref.id}")

            return student_ref.id

        except Exception:
            logger.exception("Failed to create student.")
            raise

    def get_student_by_firebase_id(self, firebase_id: str):
        try:
            student = self.collection.document(firebase_id).get()

            if not student.exists:
                return None

            data = self._student_to_dict(student)

            logger.info(f"Student retrieved successfully | Firebase ID: {firebase_id}")

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
                data = self._student_to_dict(student)
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
                data = self._student_to_dict(student)
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
                data = self._student_to_dict(student)
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
                data = self._student_to_dict(student)
                return data

            return None

        except Exception:
            logger.exception("Failed to retrieve student by phone.")
            raise

    def get_all_students(self):
        try:
            students = self._student_query().stream()

            student_list = []

            for student in students:
                student_list.append(self._student_to_dict(student))

            student_list = self._sort_students(student_list)

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
            return sum(1 for _ in self._student_query().stream())

        except Exception:
            logger.exception("Failed to count students")
            raise

    def update_student(self, student_id: str, student_data: dict):
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
                student_data = self._prepare_update_data(student_data)

                self.collection.document(student.id).update(student_data)

                logger.info(f"Student updated successfully | Student ID: {student_id}")

                return True

            return False

        except Exception:
            logger.exception("Failed to update student.")
            raise

    def search_students(self, keyword: str):
        try:
            if not keyword:
                return []

            keyword = str(keyword).strip().lower()

            if not keyword:
                return []

            students = self._student_query().stream()

            result = []

            for student in students:
                data = self._student_to_dict(student)

                searchable_fields = [
                    str(data.get("student_id", "")).lower(),
                    str(data.get("name", "")).lower(),
                    str(data.get("cnic", "")).lower(),
                    str(data.get("phone", "")).lower(),
                    str(data.get("email", "")).lower(),
                    str(data.get("guardian_name", "")).lower(),
                    str(data.get("guardian_phone", "")).lower(),
                    str(data.get("room_number", "")).lower(),
                    str(data.get("address", "")).lower(),
                    str(data.get("blood_group", "")).lower(),
                    str(data.get("bed_number", "")).lower(),
                    str(data.get("fee_status", "")).lower(),
                    str(data.get("status", "")).lower(),
                ]

                if any(keyword in field for field in searchable_fields):
                    result.append(data)

            result = self._sort_students(result)

            logger.info(
                f"Student search completed | Keyword: {keyword} | Results: {len(result)}"
            )

            return result

        except Exception:
            logger.exception("Failed to search students.")
            raise

    def disable_student(self, student_id: str):
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
                self.collection.document(student.id).update(
                    {
                        "is_active": False,
                        "updated_at": self._get_timestamp(),
                    }
                )

                logger.info(f"Student disabled successfully | Student ID: {student_id}")

                return True

            return False

        except Exception:
            logger.exception("Failed to disable student.")
            raise

    def enable_student(self, student_id: str):
        try:
            student_id = str(student_id).strip().upper()

            students = (
                self.collection
                .where("student_id", "==", student_id)
                .where("is_active", "==", False)
                .limit(1)
                .stream()
            )

            for student in students:
                self.collection.document(student.id).update(
                    {
                        "is_active": True,
                        "updated_at": self._get_timestamp(),
                    }
                )

                logger.info(f"Student enabled successfully | Student ID: {student_id}")

                return True

            return False

        except Exception:
            logger.exception("Failed to enable student.")
            raise

    def get_active_students(self):
        try:
            students = self._student_query().stream()

            student_list = []

            for student in students:
                student_list.append(self._student_to_dict(student))

            student_list = self._sort_students(student_list)

            logger.info(f"Fetched {len(student_list)} active students.")

            return student_list

        except Exception:
            logger.exception("Failed to fetch active students.")
            raise

    def get_inactive_students(self):
        try:
            students = (
                self.collection
                .where("is_active", "==", False)
                .stream()
            )

            student_list = []

            for student in students:
                data = self._student_to_dict(student)
                student_list.append(data)

            student_list = self._sort_students(student_list)

            logger.info(f"Fetched {len(student_list)} inactive students.")

            return student_list

        except Exception:
            logger.exception("Failed to fetch inactive students.")
            raise

    def get_students_by_room(self, room_firebase_id: str):
        try:
            room_firebase_id = str(room_firebase_id).strip()

            students = self._student_query().stream()

            student_list = []

            for student in students:
                data = self._student_to_dict(student)

                if data.get("room_firebase_id") == room_firebase_id:
                    student_list.append(data)

            student_list.sort(
                key=lambda x: (
                    str(x.get("bed_number", "")).upper(),
                    str(x.get("student_id", "")).upper(),
                )
            )

            logger.info(f"Fetched {len(student_list)} students for room {room_firebase_id}")

            return student_list

        except Exception:
            logger.exception("Failed to fetch students by room.")
            raise

    def get_students_without_room(self):
        try:
            students = self._student_query().stream()

            student_list = []

            for student in students:
                data = self._student_to_dict(student)

                room_id = data.get("room_firebase_id")

                if not room_id:
                    data["firebase_id"] = student.id
                    student_list.append(data)

            student_list = self._sort_students(student_list)

            logger.info(f"Fetched {len(student_list)} students without room allocation.")

            return student_list

        except Exception:
            logger.exception("Failed to fetch students without room.")
            raise

    def get_student_statistics(self):
        try:
            students = self._student_query().stream()

            stats = {
                "total_students": 0,
                "active_students": 0,
                "inactive_students": 0,
                "students_with_room": 0,
                "students_without_room": 0,
                "fee_paid": 0,
                "fee_pending": 0,
            }

            for student in students:
                data = self._student_to_dict(student)

                stats["total_students"] += 1

                if data.get("is_active", True):
                    stats["active_students"] += 1
                else:
                    stats["inactive_students"] += 1

                if data.get("room_firebase_id"):
                    stats["students_with_room"] += 1
                else:
                    stats["students_without_room"] += 1

                fee_status = str(data.get("fee_status", "")).strip().title()

                if fee_status == "Paid":
                    stats["fee_paid"] += 1
                else:
                    stats["fee_pending"] += 1

            logger.info(f"Student statistics generated successfully | {stats}")

            return stats

        except Exception:
            logger.exception("Failed to generate student statistics.")
            raise