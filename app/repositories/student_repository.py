from datetime import UTC, datetime
from typing import Optional

from firebase_admin import firestore

from app.firebase.firebase import db
from app.utils.logger import logger


class StudentRepository:

    def __init__(self):
        self.collection = db.collection("students")
        self.history_collection = db.collection("student_history")

    # ============================================================
    # BASIC HELPERS
    # ============================================================

    def _get_timestamp(self) -> str:
        return datetime.now(UTC).isoformat()

    def _normalize_id(self, value: str) -> str:
        return str(value or "").strip().upper()

    def _normalize_phone(self, value: str) -> str:
        return str(value or "").strip()

    def _normalize_cnic(self, value: str) -> str:
        return str(value or "").strip()

    def _normalize_email(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = str(value).strip().lower()

        return value or None

    def _student_query(self):
        return self.collection.where(
            "is_active",
            "==",
            True,
        )

    def _student_to_dict(self, student) -> dict:
        data = student.to_dict() or {}
        data["firebase_id"] = student.id
        return data

    def _sort_students(self, students: list[dict]) -> list[dict]:
        students.sort(
            key=lambda x: (
                str(x.get("student_id", "")).upper(),
                str(x.get("name", "")).upper(),
            )
        )
        return students

    # ============================================================
    # VALIDATION / NORMALIZATION
    # ============================================================

    def _normalize_student_data(self, student_data: dict) -> dict:
        if not isinstance(student_data, dict):
            raise ValueError("Student data must be a dictionary.")

        normalized = dict(student_data)

        # --------------------------------------------------------
        # IDs
        # --------------------------------------------------------

        if "student_id" in normalized:
            student_id = self._normalize_id(
                normalized.get("student_id")
            )

            if not student_id:
                raise ValueError("Student ID cannot be empty.")

            normalized["student_id"] = student_id

        # --------------------------------------------------------
        # PERSONAL
        # --------------------------------------------------------

        if "name" in normalized:
            name = str(normalized.get("name") or "").strip()

            if not name:
                raise ValueError("Student name cannot be empty.")

            normalized["name"] = name.title()

        if "cnic" in normalized:
            cnic = self._normalize_cnic(
                normalized.get("cnic")
            )

            if not cnic:
                raise ValueError("CNIC cannot be empty.")

            if not cnic.isdigit() or len(cnic) != 13:
                raise ValueError(
                    "CNIC must contain exactly 13 digits."
                )

            normalized["cnic"] = cnic

        if "phone" in normalized:
            phone = self._normalize_phone(
                normalized.get("phone")
            )

            if not phone:
                raise ValueError("Phone number cannot be empty.")

            if (
                not phone.startswith("03")
                or len(phone) != 11
                or not phone.isdigit()
            ):
                raise ValueError(
                    "Phone number must be a valid Pakistani mobile number."
                )

            normalized["phone"] = phone

        if "email" in normalized:
            normalized["email"] = self._normalize_email(
                normalized.get("email")
            )

        if "blood_group" in normalized:
            if normalized["blood_group"] is not None:
                blood_group = (
                    str(normalized["blood_group"])
                    .strip()
                    .upper()
                )

                allowed_blood_groups = {
                    "A+",
                    "A-",
                    "B+",
                    "B-",
                    "AB+",
                    "AB-",
                    "O+",
                    "O-",
                }

                if blood_group not in allowed_blood_groups:
                    raise ValueError(
                        "Invalid blood group."
                    )

                normalized["blood_group"] = blood_group

        if "address" in normalized:
            address = str(
                normalized.get("address") or ""
            ).strip()

            if not address:
                raise ValueError(
                    "Address cannot be empty."
                )

            normalized["address"] = address

        # --------------------------------------------------------
        # GUARDIAN
        # --------------------------------------------------------

        if "guardian_name" in normalized:
            guardian_name = str(
                normalized.get("guardian_name") or ""
            ).strip()

            if not guardian_name:
                raise ValueError(
                    "Guardian name cannot be empty."
                )

            normalized["guardian_name"] = guardian_name.title()

        if "guardian_phone" in normalized:
            guardian_phone = self._normalize_phone(
                normalized.get("guardian_phone")
            )

            if (
                not guardian_phone.startswith("03")
                or len(guardian_phone) != 11
                or not guardian_phone.isdigit()
            ):
                raise ValueError(
                    "Guardian phone number is invalid."
                )

            normalized["guardian_phone"] = guardian_phone

        if "guardian_cnic" in normalized:
            guardian_cnic = self._normalize_cnic(
                normalized.get("guardian_cnic")
            )

            if (
                not guardian_cnic.isdigit()
                or len(guardian_cnic) != 13
            ):
                raise ValueError(
                    "Guardian CNIC must contain exactly 13 digits."
                )

            normalized["guardian_cnic"] = guardian_cnic

        if "relation" in normalized:
            if normalized["relation"] is not None:
                normalized["relation"] = (
                    str(normalized["relation"])
                    .strip()
                    .title()
                )

        # --------------------------------------------------------
        # ROOM / ALLOCATION
        # --------------------------------------------------------

        if "room_firebase_id" in normalized:
            value = normalized.get("room_firebase_id")

            if value is not None:
                normalized["room_firebase_id"] = (
                    str(value).strip()
                )

        if "room_number" in normalized:
            value = normalized.get("room_number")

            if value is not None:
                normalized["room_number"] = (
                    str(value).strip().upper()
                )

        if "floor" in normalized:
            value = normalized.get("floor")

            if value is not None:
                try:
                    floor = int(value)
                except (TypeError, ValueError):
                    raise ValueError(
                        "Floor must be a valid integer."
                    )

                if floor < 0:
                    raise ValueError(
                        "Floor cannot be negative."
                    )

                normalized["floor"] = floor

        if "bed_number" in normalized:
            value = normalized.get("bed_number")

            if value is not None:
                normalized["bed_number"] = (
                    str(value).strip().upper()
                )

        if "block" in normalized:
            value = normalized.get("block")

            if value is not None:
                normalized["block"] = (
                    str(value).strip().upper()
                )

        if "room_type" in normalized:
            value = normalized.get("room_type")

            if value is not None:
                normalized["room_type"] = (
                    str(value).strip().title()
                )

        # --------------------------------------------------------
        # FINANCIAL
        # --------------------------------------------------------

        for field in (
            "monthly_fee",
            "security_deposit",
            "pending_fee",
        ):
            if field in normalized:
                value = normalized.get(field)

                if value is None:
                    continue

                try:
                    value = float(value)
                except (TypeError, ValueError):
                    raise ValueError(
                        f"{field} must be a valid number."
                    )

                if value < 0:
                    raise ValueError(
                        f"{field} cannot be negative."
                    )

                normalized[field] = value

        # --------------------------------------------------------
        # STATUS
        # --------------------------------------------------------

        if "status" in normalized:
            status = normalized.get("status")

            if hasattr(status, "value"):
                status = status.value

            status = str(status).strip().title()

            if status not in {
                "Active",
                "Inactive",
            }:
                raise ValueError(
                    "Invalid student status."
                )

            normalized["status"] = status

        if "fee_status" in normalized:
            fee_status = normalized.get("fee_status")

            if hasattr(fee_status, "value"):
                fee_status = fee_status.value

            fee_status = (
                str(fee_status)
                .strip()
                .title()
            )

            if fee_status not in {
                "Paid",
                "Pending",
            }:
                raise ValueError(
                    "Invalid fee status."
                )

            normalized["fee_status"] = fee_status

        # --------------------------------------------------------
        # DATES / REMARKS
        # --------------------------------------------------------

        if "joining_date" in normalized:
            value = normalized.get("joining_date")

            if value is not None:
                value = str(value).strip()

                if not value:
                    raise ValueError(
                        "Joining date cannot be empty."
                    )

                normalized["joining_date"] = value

        if "remarks" in normalized:
            value = normalized.get("remarks")

            if value is not None:
                normalized["remarks"] = (
                    str(value).strip()
                )

        # --------------------------------------------------------
        # IMAGES
        # --------------------------------------------------------

        for field in (
            "profile_image",
            "cnic_front_image",
            "cnic_back_image",
        ):
            if field in normalized:
                value = normalized.get(field)

                if value is not None:
                    normalized[field] = (
                        str(value).strip()
                    )

        return normalized

    # ============================================================
    # CREATE PREPARATION
    # ============================================================

    def _prepare_student_data(
        self,
        student_data: dict,
    ) -> dict:

        student_data = self._normalize_student_data(
            student_data
        )

        timestamp = self._get_timestamp()

        student_data.setdefault(
            "is_active",
            True,
        )

        student_data.setdefault(
            "status",
            "Active",
        )

        student_data.setdefault(
            "monthly_fee",
            0.0,
        )

        student_data.setdefault(
            "security_deposit",
            0.0,
        )

        student_data.setdefault(
            "pending_fee",
            0.0,
        )

        student_data.setdefault(
            "fee_status",
            "Pending",
        )

        student_data.setdefault(
            "room_firebase_id",
            None,
        )

        student_data.setdefault(
            "room_number",
            None,
        )

        student_data.setdefault(
            "floor",
            None,
        )

        student_data.setdefault(
            "bed_number",
            None,
        )

        student_data.setdefault(
            "created_at",
            timestamp,
        )

        student_data["updated_at"] = timestamp

        # Active flag and status must remain synchronized.
        if student_data["status"] == "Inactive":
            student_data["is_active"] = False

        if student_data["status"] == "Active":
            student_data["is_active"] = True

        return student_data

    # ============================================================
    # UPDATE PREPARATION
    # ============================================================

    def _prepare_update_data(
        self,
        student_data: dict,
    ) -> dict:

        student_data = self._normalize_student_data(
            student_data
        )

        # Protected fields
        student_data.pop(
            "student_id",
            None,
        )

        student_data.pop(
            "created_at",
            None,
        )

        student_data.pop(
            "firebase_id",
            None,
        )

        student_data["updated_at"] = (
            self._get_timestamp()
        )

        # Keep status and is_active synchronized.
        if "status" in student_data:

            if student_data["status"] == "Active":
                student_data["is_active"] = True

            elif student_data["status"] == "Inactive":
                student_data["is_active"] = False

        return student_data

    # ============================================================
    # DUPLICATE CHECKS
    # ============================================================

    def _find_active_by_field(
        self,
        field: str,
        value: str,
        exclude_firebase_id: Optional[str] = None,
    ):

        query = (
            self.collection
            .where(field, "==", value)
            .where("is_active", "==", True)
            .limit(10)
        )

        for student in query.stream():

            if (
                exclude_firebase_id
                and student.id == exclude_firebase_id
            ):
                continue

            return self._student_to_dict(student)

        return None

    def validate_unique_student(
        self,
        student_data: dict,
        exclude_firebase_id: Optional[str] = None,
    ):
        cnic = student_data.get("cnic")

        if cnic:
            if self._find_active_by_field(
                "cnic",
                cnic,
                exclude_firebase_id,
            ):
                raise ValueError(
                    "A student with this CNIC already exists."
                )

        phone = student_data.get("phone")

        if phone:
            if self._find_active_by_field(
                "phone",
                phone,
                exclude_firebase_id,
            ):
                raise ValueError(
                    "A student with this phone number already exists."
                )

        email = student_data.get("email")

        if email:
            if self._find_active_by_field(
                "email",
                email,
                exclude_firebase_id,
            ):
                raise ValueError(
                    "A student with this email already exists."
                )

    # ============================================================
    # CREATE STUDENT
    # ============================================================

    def create_student(
        self,
        student_data: dict,
    ):
        try:

            prepared_data = self._prepare_student_data(
                student_data
            )

            self.validate_unique_student(
                prepared_data
            )

            student_id = prepared_data.get(
                "student_id"
            )

            if student_id:
                existing = self.get_student_by_student_id(
                    student_id
                )

                if existing:
                    raise ValueError(
                        "Student ID already exists."
                    )

            student_ref = self.collection.document()

            student_ref.set(
                prepared_data
            )

            logger.info(
                "Student created successfully | "
                f"Firebase ID: {student_ref.id}"
            )

            return student_ref.id

        except Exception:
            logger.exception(
                "Failed to create student."
            )
            raise

    # ============================================================
    # GET BY FIREBASE ID
    # ============================================================

    def get_student_by_firebase_id(
        self,
        firebase_id: str,
    ):
        try:

            firebase_id = str(
                firebase_id or ""
            ).strip()

            if not firebase_id:
                return None

            student = (
                self.collection
                .document(firebase_id)
                .get()
            )

            if not student.exists:
                return None

            return self._student_to_dict(
                student
            )

        except Exception:
            logger.exception(
                "Failed to retrieve student by Firebase ID."
            )
            raise

    # ============================================================
    # GET BY EMAIL
    # ============================================================

    def get_student_by_email(
        self,
        email: str,
    ):
        try:

            email = self._normalize_email(
                email
            )

            if not email:
                return None

            return self._find_active_by_field(
                "email",
                email,
            )

        except Exception:
            logger.exception(
                "Failed to retrieve student by email."
            )
            raise

    # ============================================================
    # GET BY STUDENT ID
    # ============================================================

    def get_student_by_student_id(
        self,
        student_id: str,
    ):
        try:

            student_id = self._normalize_id(
                student_id
            )

            if not student_id:
                return None

            students = (
                self.collection
                .where(
                    "student_id",
                    "==",
                    student_id,
                )
                .where(
                    "is_active",
                    "==",
                    True,
                )
                .limit(1)
                .stream()
            )

            for student in students:
                return self._student_to_dict(
                    student
                )

            return None

        except Exception:
            logger.exception(
                "Failed to retrieve student by Student ID."
            )
            raise

    # ============================================================
    # GET BY CNIC
    # ============================================================

    def get_student_by_cnic(
        self,
        cnic: str,
    ):
        try:

            cnic = self._normalize_cnic(
                cnic
            )

            if not cnic:
                return None

            return self._find_active_by_field(
                "cnic",
                cnic,
            )

        except Exception:
            logger.exception(
                "Failed to retrieve student by CNIC."
            )
            raise

    # ============================================================
    # GET BY PHONE
    # ============================================================

    def get_student_by_phone(
        self,
        phone: str,
    ):
        try:

            phone = self._normalize_phone(
                phone
            )

            if not phone:
                return None

            return self._find_active_by_field(
                "phone",
                phone,
            )

        except Exception:
            logger.exception(
                "Failed to retrieve student by phone."
            )
            raise

    # ============================================================
    # GET ALL ACTIVE STUDENTS
    # ============================================================

    def get_all_students(self):
        try:

            students = (
                self._student_query()
                .stream()
            )

            student_list = [
                self._student_to_dict(student)
                for student in students
            ]

            return self._sort_students(
                student_list
            )

        except Exception:
            logger.exception(
                "Failed to fetch students."
            )
            raise

    # ============================================================
    # STUDENT EXISTS
    # ============================================================

    def student_exists(
        self,
        student_id: str,
    ) -> bool:

        try:

            return (
                self.get_student_by_student_id(
                    student_id
                )
                is not None
            )

        except Exception:
            logger.exception(
                "Failed to check student existence."
            )
            raise

    # ============================================================
    # COUNT
    # ============================================================

    def count_students(self):
        try:

            return sum(
                1
                for _ in self._student_query().stream()
            )

        except Exception:
            logger.exception(
                "Failed to count students."
            )
            raise

    # ============================================================
    # UPDATE STUDENT
    # ============================================================

    def update_student(
        self,
        student_id: str,
        student_data: dict,
    ):
        try:

            student_id = self._normalize_id(
                student_id
            )

            if not student_id:
                raise ValueError(
                    "Student ID is required."
                )

            students = (
                self.collection
                .where(
                    "student_id",
                    "==",
                    student_id,
                )
                .where(
                    "is_active",
                    "==",
                    True,
                )
                .limit(1)
                .stream()
            )

            for student in students:

                prepared_data = (
                    self._prepare_update_data(
                        student_data
                    )
                )

                if not prepared_data:
                    raise ValueError(
                        "No valid fields provided for update."
                    )

                self.validate_unique_student(
                    prepared_data,
                    exclude_firebase_id=student.id,
                )

                self.collection.document(
                    student.id
                ).update(
                    prepared_data
                )

                logger.info(
                    "Student updated successfully | "
                    f"Student ID: {student_id}"
                )

                return True

            return False

        except Exception:
            logger.exception(
                "Failed to update student."
            )
            raise

    # ============================================================
    # SEARCH
    # ============================================================

    def search_students(
        self,
        keyword: str,
    ):
        try:

            keyword = str(
                keyword or ""
            ).strip().lower()

            if not keyword:
                return []

            students = (
                self._student_query()
                .stream()
            )

            result = []

            for student in students:

                data = self._student_to_dict(
                    student
                )

                searchable_fields = [
                    "student_id",
                    "name",
                    "cnic",
                    "phone",
                    "email",
                    "guardian_name",
                    "guardian_phone",
                    "room_number",
                    "address",
                    "blood_group",
                    "bed_number",
                    "fee_status",
                    "status",
                ]

                searchable_values = [
                    str(
                        data.get(field, "")
                    ).lower()
                    for field in searchable_fields
                ]

                if any(
                    keyword in value
                    for value in searchable_values
                ):
                    result.append(data)

            return self._sort_students(
                result
            )

        except Exception:
            logger.exception(
                "Failed to search students."
            )
            raise

    # ============================================================
    # DISABLE STUDENT
    # ============================================================

    def disable_student(
        self,
        student_id: str,
    ):
        try:

            student_id = self._normalize_id(
                student_id
            )

            students = (
                self.collection
                .where(
                    "student_id",
                    "==",
                    student_id,
                )
                .where(
                    "is_active",
                    "==",
                    True,
                )
                .limit(1)
                .stream()
            )

            for student in students:

                student_ref = (
                    self.collection.document(
                        student.id
                    )
                )

                timestamp = (
                    self._get_timestamp()
                )

                student_ref.update(
                    {
                        "is_active": False,
                        "status": "Inactive",
                        "updated_at": timestamp,
                    }
                )

                logger.info(
                    "Student disabled successfully | "
                    f"Student ID: {student_id}"
                )

                return True

            return False

        except Exception:
            logger.exception(
                "Failed to disable student."
            )
            raise

    # ============================================================
    # ENABLE STUDENT
    # ============================================================

    def enable_student(
        self,
        student_id: str,
    ):
        try:

            student_id = self._normalize_id(
                student_id
            )

            students = (
                self.collection
                .where(
                    "student_id",
                    "==",
                    student_id,
                )
                .where(
                    "is_active",
                    "==",
                    False,
                )
                .limit(1)
                .stream()
            )

            for student in students:

                student_ref = (
                    self.collection.document(
                        student.id
                    )
                )

                timestamp = (
                    self._get_timestamp()
                )

                student_ref.update(
                    {
                        "is_active": True,
                        "status": "Active",
                        "updated_at": timestamp,
                    }
                )

                logger.info(
                    "Student enabled successfully | "
                    f"Student ID: {student_id}"
                )

                return True

            return False

        except Exception:
            logger.exception(
                "Failed to enable student."
            )
            raise

    # ============================================================
    # ACTIVE STUDENTS
    # ============================================================

    def get_active_students(self):
        return self.get_all_students()

    # ============================================================
    # INACTIVE / ALUMNI STUDENTS
    # ============================================================

    def get_inactive_students(self):
        try:

            students = (
                self.collection
                .where(
                    "is_active",
                    "==",
                    False,
                )
                .stream()
            )

            result = [
                self._student_to_dict(student)
                for student in students
            ]

            return self._sort_students(
                result
            )

        except Exception:
            logger.exception(
                "Failed to fetch inactive students."
            )
            raise

    # ============================================================
    # STUDENTS BY ROOM
    # ============================================================

    def get_students_by_room(
        self,
        room_firebase_id: str,
    ):
        try:

            room_firebase_id = str(
                room_firebase_id or ""
            ).strip()

            if not room_firebase_id:
                return []

            students = (
                self.collection
                .where(
                    "room_firebase_id",
                    "==",
                    room_firebase_id,
                )
                .where(
                    "is_active",
                    "==",
                    True,
                )
                .stream()
            )

            result = [
                self._student_to_dict(student)
                for student in students
            ]

            result.sort(
                key=lambda x: (
                    str(
                        x.get(
                            "bed_number",
                            "",
                        )
                    ).upper(),
                    str(
                        x.get(
                            "student_id",
                            "",
                        )
                    ).upper(),
                )
            )

            return result

        except Exception:
            logger.exception(
                "Failed to fetch students by room."
            )
            raise

    # ============================================================
    # STUDENTS WITHOUT ROOM
    # ============================================================

    def get_students_without_room(self):
        try:

            students = (
                self._student_query()
                .stream()
            )

            result = []

            for student in students:

                data = self._student_to_dict(
                    student
                )

                if not data.get(
                    "room_firebase_id"
                ):
                    result.append(data)

            return self._sort_students(
                result
            )

        except Exception:
            logger.exception(
                "Failed to fetch students without room."
            )
            raise

    # ============================================================
    # STUDENT HISTORY
    # ============================================================

    def add_student_history(
        self,
        student_id: str,
        action: str,
        details: Optional[dict] = None,
    ):
        """
        Creates a permanent history record.

        IMPORTANT:
        This record is never overwritten when the student
        changes room, pays fee, leaves hostel, etc.
        """

        try:

            student_id = self._normalize_id(
                student_id
            )

            if not student_id:
                raise ValueError(
                    "Student ID is required."
                )

            action = str(
                action or ""
            ).strip()

            if not action:
                raise ValueError(
                    "History action is required."
                )

            history_data = {
                "student_id": student_id,
                "action": action,
                "details": details or {},
                "created_at": self._get_timestamp(),
            }

            history_ref = (
                self.history_collection.document()
            )

            history_ref.set(
                history_data
            )

            logger.info(
                "Student history created | "
                f"Student ID: {student_id} | "
                f"Action: {action}"
            )

            return history_ref.id

        except Exception:
            logger.exception(
                "Failed to create student history."
            )
            raise

    # ============================================================
    # GET STUDENT HISTORY
    # ============================================================

    def get_student_history(
        self,
        student_id: str,
    ):
        try:

            student_id = self._normalize_id(
                student_id
            )

            if not student_id:
                return []

            history = (
                self.history_collection
                .where(
                    "student_id",
                    "==",
                    student_id,
                )
                .stream()
            )

            result = []

            for record in history:

                data = record.to_dict() or {}

                data["firebase_id"] = (
                    record.id
                )

                result.append(data)

            result.sort(
                key=lambda x: str(
                    x.get(
                        "created_at",
                        "",
                    )
                ),
                reverse=True,
            )

            return result

        except Exception:
            logger.exception(
                "Failed to retrieve student history."
            )
            raise

    # ============================================================
    # STUDENT STATISTICS
    # ============================================================

    def get_student_statistics(self):
        try:

            students = (
                self.collection
                .stream()
            )

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

                data = self._student_to_dict(
                    student
                )

                stats[
                    "total_students"
                ] += 1

                is_active = bool(
                    data.get(
                        "is_active",
                        True,
                    )
                )

                if is_active:
                    stats[
                        "active_students"
                    ] += 1
                else:
                    stats[
                        "inactive_students"
                    ] += 1

                if data.get(
                    "room_firebase_id"
                ):
                    stats[
                        "students_with_room"
                    ] += 1
                else:
                    stats[
                        "students_without_room"
                    ] += 1

                fee_status = str(
                    data.get(
                        "fee_status",
                        "Pending",
                    )
                ).strip().title()

                if fee_status == "Paid":
                    stats[
                        "fee_paid"
                    ] += 1
                else:
                    stats[
                        "fee_pending"
                    ] += 1

            return stats

        except Exception:
            logger.exception(
                "Failed to generate student statistics."
            )
            raise