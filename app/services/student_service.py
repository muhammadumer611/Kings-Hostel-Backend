from typing import Any

from app.repositories.student_repository import StudentRepository
from app.services.room_service import RoomService
from app.utils.student_id_generator import StudentIDGenerator
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class StudentService:

    def __init__(self):
        self.repository = StudentRepository()
        self.room_service = RoomService()
        self.id_generator = StudentIDGenerator()

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @staticmethod
    def _clean_string(value: Any) -> str | None:
        if value is None:
            return None

        value = str(value).strip()

        return value if value else None

    @staticmethod
    def _clean_upper(value: Any) -> str | None:
        value = StudentService._clean_string(value)

        return value.upper() if value else None

    @staticmethod
    def _clean_lower(value: Any) -> str | None:
        value = StudentService._clean_string(value)

        return value.lower() if value else None

    @staticmethod
    def _enum_value(value: Any, default: str | None = None) -> str | None:
        if value is None:
            return default

        if hasattr(value, "value"):
            return str(value.value)

        value = str(value).strip()

        return value if value else default

    @staticmethod
    def _normalize_money(
        value: Any,
        field_name: str,
        allow_zero: bool = True,
    ) -> float | None:

        if value is None:
            return None

        try:
            amount = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field_name} must be a valid number.")

        if amount < 0:
            raise ValueError(f"{field_name} cannot be negative.")

        if not allow_zero and amount <= 0:
            raise ValueError(f"{field_name} must be greater than 0.")

        return round(amount, 2)

    # ============================================================
    # PAYLOAD NORMALIZATION
    # ============================================================

    def _normalize_student_data(self, student_data: dict) -> dict:

        if not isinstance(student_data, dict):
            raise ValueError("Student payload must be a dictionary.")

        personal = student_data.get("personal")
        guardian = student_data.get("guardian")
        allocation = student_data.get("allocation")

        # --------------------------------------------------------
        # NEW NESTED PAYLOAD
        # --------------------------------------------------------

        if (
            "personal" in student_data
            or "guardian" in student_data
            or "allocation" in student_data
        ):

            personal = personal or {}
            guardian = guardian or {}
            allocation = allocation or {}

            if not isinstance(personal, dict):
                raise ValueError("Personal data must be an object.")

            if not isinstance(guardian, dict):
                raise ValueError("Guardian data must be an object.")

            if not isinstance(allocation, dict):
                raise ValueError("Allocation data must be an object.")

            return {
                "name": self._clean_string(
                    personal.get("name")
                ),

                "cnic": self._clean_string(
                    personal.get("cnic")
                ),

                "phone": self._clean_string(
                    personal.get("phone")
                ),

                "email": self._clean_lower(
                    personal.get("email")
                ),

                "blood_group": self._clean_upper(
                    personal.get("blood_group")
                    if "blood_group" in personal
                    else personal.get("bloodGroup")
                ),

                "address": self._clean_string(
                    personal.get("address")
                ),

                "profile_image": self._clean_string(
                    personal.get("profile_image")
                    if "profile_image" in personal
                    else personal.get("profileImage")
                ),

                "cnic_front_image": self._clean_string(
                    personal.get("cnic_front_image")
                    if "cnic_front_image" in personal
                    else personal.get("cnicFrontImage")
                ),

                "cnic_back_image": self._clean_string(
                    personal.get("cnic_back_image")
                    if "cnic_back_image" in personal
                    else personal.get("cnicBackImage")
                ),

                "guardian_name": self._clean_string(
                    guardian.get("guardian_name")
                    if "guardian_name" in guardian
                    else guardian.get("name")
                ),

                "guardian_phone": self._clean_string(
                    guardian.get("guardian_phone")
                    if "guardian_phone" in guardian
                    else guardian.get("phone")
                ),

                "guardian_cnic": self._clean_string(
                    guardian.get("guardian_cnic")
                    if "guardian_cnic" in guardian
                    else guardian.get("cnic")
                ),

                "relation": self._clean_string(
                    guardian.get("relation")
                ),

                "block": self._clean_upper(
                    allocation.get("block")
                ),

                "room_type": self._clean_string(
                    allocation.get("room_type")
                    if "room_type" in allocation
                    else allocation.get("roomType")
                ),

                "room_firebase_id": self._clean_string(
                    allocation.get("room_firebase_id")
                    if "room_firebase_id" in allocation
                    else allocation.get("roomFirebaseId")
                ),

                "room_number": self._clean_upper(
                    allocation.get("room_number")
                    if "room_number" in allocation
                    else allocation.get("roomNumber")
                ),

                "floor": allocation.get("floor"),

                "bed_number": self._clean_upper(
                    allocation.get("bed_number")
                    if "bed_number" in allocation
                    else allocation.get("bedNumber")
                ),

                "joining_date": self._clean_string(
                    allocation.get("joining_date")
                    if "joining_date" in allocation
                    else allocation.get("joiningDate")
                ),

                "remarks": self._clean_string(
                    allocation.get("remarks")
                ),

                "monthly_fee": allocation.get("monthly_fee")
                if "monthly_fee" in allocation
                else allocation.get("monthlyFee"),

                "security_deposit": allocation.get("security_deposit")
                if "security_deposit" in allocation
                else allocation.get("securityDeposit"),

                "status": self._enum_value(
                    student_data.get("status"),
                    "Active",
                ),
            }

        # --------------------------------------------------------
        # LEGACY PAYLOAD
        # --------------------------------------------------------

        return {
            "name": self._clean_string(
                student_data.get("name")
                or student_data.get("full_name")
            ),

            "cnic": self._clean_string(
                student_data.get("cnic")
            ),

            "phone": self._clean_string(
                student_data.get("phone")
            ),

            "email": self._clean_lower(
                student_data.get("email")
            ),

            "blood_group": self._clean_upper(
                student_data.get("blood_group")
            ),

            "address": self._clean_string(
                student_data.get("address")
            ),

            "profile_image": self._clean_string(
                student_data.get("profile_image")
            ),

            "cnic_front_image": self._clean_string(
                student_data.get("cnic_front_image")
            ),

            "cnic_back_image": self._clean_string(
                student_data.get("cnic_back_image")
            ),

            "guardian_name": self._clean_string(
                student_data.get("guardian_name")
                or student_data.get("father_name")
            ),

            "guardian_phone": self._clean_string(
                student_data.get("guardian_phone")
            ),

            "guardian_cnic": self._clean_string(
                student_data.get("guardian_cnic")
            ),

            "relation": self._clean_string(
                student_data.get("relation")
            ),

            "block": self._clean_upper(
                student_data.get("block")
            ),

            "room_type": self._clean_string(
                student_data.get("room_type")
            ),

            "room_firebase_id": self._clean_string(
                student_data.get("room_firebase_id")
            ),

            "room_number": self._clean_upper(
                student_data.get("room_number")
            ),

            "floor": student_data.get("floor"),

            "bed_number": self._clean_upper(
                student_data.get("bed_number")
            ),

            "joining_date": self._clean_string(
                student_data.get("joining_date")
            ),

            "remarks": self._clean_string(
                student_data.get("remarks")
            ),

            "monthly_fee": student_data.get("monthly_fee"),

            "security_deposit": student_data.get("security_deposit"),

            "status": self._enum_value(
                student_data.get("status"),
                "Active",
            ),
        }

    # ============================================================
    # VALIDATION
    # ============================================================

    def _validate_student_data(
        self,
        student_data: dict,
        is_create: bool = True,
    ) -> None:

        if not isinstance(student_data, dict):
            raise ValueError("Invalid student data.")

        if is_create:

            required_fields = {
                "name": "Student name is required.",
                "cnic": "CNIC is required.",
                "phone": "Phone number is required.",
                "guardian_name": "Guardian name is required.",
                "guardian_phone": "Guardian phone is required.",
                "guardian_cnic": "Guardian CNIC is required.",
                "address": "Address is required.",
            }

            for field, message in required_fields.items():
                if not self._clean_string(student_data.get(field)):
                    raise ValueError(message)

        if student_data.get("floor") is not None:
            try:
                floor = int(student_data["floor"])
            except (TypeError, ValueError):
                raise ValueError("Floor must be a valid number.")

            if floor < 0:
                raise ValueError("Floor cannot be negative.")

            student_data["floor"] = floor

        if "monthly_fee" in student_data:
            student_data["monthly_fee"] = self._normalize_money(
                student_data.get("monthly_fee"),
                "Monthly fee",
                allow_zero=True,
            )

        if "security_deposit" in student_data:
            student_data["security_deposit"] = self._normalize_money(
                student_data.get("security_deposit"),
                "Security deposit",
                allow_zero=True,
            )

    # ============================================================
    # UNIQUE FIELD VALIDATION
    # ============================================================

    def _check_unique_fields(
        self,
        student_data: dict,
        current_student: dict | None = None,
    ) -> None:

        current_cnic = current_student.get("cnic") if current_student else None
        current_phone = current_student.get("phone") if current_student else None
        current_email = current_student.get("email") if current_student else None

        cnic = student_data.get("cnic")

        if cnic and cnic != current_cnic:

            existing = self.repository.get_student_by_cnic(cnic)

            if existing:
                existing_id = existing.get("student_id")

                if not current_student or existing_id != current_student.get(
                    "student_id"
                ):
                    raise ValueError(
                        "Student with this CNIC already exists."
                    )

        phone = student_data.get("phone")

        if phone and phone != current_phone:

            existing = self.repository.get_student_by_phone(phone)

            if existing:
                existing_id = existing.get("student_id")

                if not current_student or existing_id != current_student.get(
                    "student_id"
                ):
                    raise ValueError(
                        "Phone number already exists."
                    )

        email = student_data.get("email")

        if email and email != current_email:

            existing = self.repository.get_student_by_email(email)

            if existing:
                existing_id = existing.get("student_id")

                if not current_student or existing_id != current_student.get(
                    "student_id"
                ):
                    raise ValueError(
                        "Email already exists."
                    )

    # ============================================================
    # ROOM VALIDATION
    # ============================================================

    def _validate_room_allocation(
        self,
        allocation: dict,
    ) -> None:

        room_id = allocation.get("room_firebase_id")

        if not room_id:
            return

        response = self.room_service.get_room_for_allocation(room_id)

        if not response.get("success"):
            raise ValueError(
                response.get("message", "Room is not available.")
            )

        room = response.get("data") or {}

        if not room.get("is_active", True):
            raise ValueError("Selected room is disabled.")

        if room.get("available_beds", 0) <= 0:
            raise ValueError("Selected room is already full.")

        room_number = allocation.get("room_number")

        if room_number:
            actual_room_number = str(
                room.get("room_number", "")
            ).strip().upper()

            if actual_room_number != room_number:
                raise ValueError(
                    "Selected room number does not match room."
                )

        floor = allocation.get("floor")

        if floor is not None:
            if room.get("floor") != floor:
                raise ValueError(
                    "Selected room floor does not match room."
                )

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def _serialize_student(self, student: dict) -> dict:

        if not student:
            return {}

        created_at = student.get("created_at")
        updated_at = student.get("updated_at")

        status = student.get("status", "Active")
        fee_status = student.get("fee_status", "Pending")

        if hasattr(status, "value"):
            status = status.value

        if hasattr(fee_status, "value"):
            fee_status = fee_status.value

        return {
            "student_id": student.get("student_id"),
            "firebase_id": student.get("firebase_id"),

            "name": student.get("name", ""),
            "cnic": student.get("cnic", ""),
            "phone": student.get("phone", ""),
            "email": student.get("email"),

            "blood_group": student.get("blood_group"),
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
            "room_number": student.get("room_number"),
            "floor": student.get("floor"),
            "bed_number": student.get("bed_number"),

            "monthly_fee": float(
                student.get("monthly_fee", 0) or 0
            ),

            "security_deposit": float(
                student.get("security_deposit", 0) or 0
            ),

            "pending_fee": float(
                student.get("pending_fee", 0) or 0
            ),

            "fee_status": fee_status,

            "status": status,

            "joining_date": student.get("joining_date"),
            "remarks": student.get("remarks"),

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

    # ============================================================
    # CREATE
    # ============================================================

    def create_student(self, student_data: dict):

        try:
            normalized = self._normalize_student_data(student_data)

            self._validate_student_data(
                normalized,
                is_create=True,
            )

            self._check_unique_fields(normalized)

            # Validate room before creating student.
            self._validate_room_allocation(normalized)

            # Generate unique student ID.
            student_id = self.id_generator.generate()

            max_attempts = 20

            for _ in range(max_attempts):

                if not self.repository.student_exists(student_id):
                    break

                student_id = self.id_generator.generate()

            else:
                logger.error(
                    "Unable to generate unique student ID."
                )

                return APIResponse.error(
                    "Unable to generate student ID."
                )

            normalized["student_id"] = student_id

            firebase_id = self.repository.create_student(
                normalized
            )

            # ----------------------------------------------------
            # Room allocation synchronization
            # ----------------------------------------------------

            room_id = normalized.get("room_firebase_id")

            if room_id:

                room_response = (
                    self.room_service.assign_student_to_room(
                        room_id,
                        student_id,
                    )
                )

                if not room_response.get("success"):

                    logger.error(
                        "Student created but room allocation failed | "
                        f"Student ID: {student_id} | "
                        f"Room ID: {room_id}"
                    )

                    # Roll back student using soft delete.
                    self.repository.disable_student(student_id)

                    return APIResponse.error(
                        room_response.get(
                            "message",
                            "Unable to allocate room."
                        )
                    )

            logger.info(
                "Student created successfully | "
                f"Student ID: {student_id} | "
                f"Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                "Student added successfully.",
                {
                    "student_id": student_id,
                    "firebase_id": firebase_id,
                },
            )

        except ValueError as exc:

            logger.warning(
                f"Student validation failed | {exc}"
            )

            return APIResponse.error(str(exc))

        except Exception as exc:

            logger.exception(
                "Failed to create student."
            )

            return APIResponse.error(
                "Unable to create student.",
                str(exc),
            )

    # ============================================================
    # GET ALL
    # ============================================================

    def get_all_students(self):

        try:
            students = self.repository.get_all_students()

            serialized = [
                self._serialize_student(student)
                for student in students
            ]

            return APIResponse.success(
                "Students retrieved successfully.",
                {
                    "total_students": len(serialized),
                    "students": serialized,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve students."
            )

            return APIResponse.error(
                "Unable to retrieve students.",
                str(exc),
            )

    # ============================================================
    # GET BY ID
    # ============================================================

    def get_student_by_id(self, student_id: str):

        try:

            student_id = self._clean_upper(student_id)

            if not student_id:
                return APIResponse.error(
                    "Student ID is required."
                )

            student = (
                self.repository
                .get_student_by_student_id(student_id)
            )

            if not student:

                logger.warning(
                    f"Student not found | Student ID: {student_id}"
                )

                return APIResponse.error(
                    "Student not found."
                )

            return APIResponse.success(
                "Student retrieved successfully.",
                self._serialize_student(student),
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve student."
            )

            return APIResponse.error(
                "Unable to retrieve student.",
                str(exc),
            )

    # ============================================================
    # UPDATE
    # ============================================================

    def update_student(
        self,
        student_id: str,
        student_data: dict,
    ):

        try:

            student_id = self._clean_upper(student_id)

            if not student_id:
                return APIResponse.error(
                    "Student ID is required."
                )

            existing_student = (
                self.repository
                .get_student_by_student_id(student_id)
            )

            if not existing_student:

                return APIResponse.error(
                    "Student not found."
                )

            if not isinstance(student_data, dict):

                return APIResponse.error(
                    "Invalid update payload."
                )

            update_data = {}

            # ----------------------------------------------------
            # PERSONAL
            # ----------------------------------------------------

            if "personal" in student_data:

                personal = student_data.get("personal") or {}

                if not isinstance(personal, dict):
                    return APIResponse.error(
                        "Personal data must be an object."
                    )

                field_map = {
                    "name": "name",
                    "cnic": "cnic",
                    "phone": "phone",
                    "email": "email",
                    "address": "address",
                    "profile_image": "profile_image",
                    "cnic_front_image": "cnic_front_image",
                    "cnic_back_image": "cnic_back_image",
                }

                for source, target in field_map.items():

                    if source in personal:
                        value = personal[source]

                        if source == "email":
                            value = self._clean_lower(value)
                        else:
                            value = self._clean_string(value)

                        update_data[target] = value

                if "blood_group" in personal:
                    update_data["blood_group"] = (
                        self._clean_upper(
                            personal["blood_group"]
                        )
                    )

            # ----------------------------------------------------
            # GUARDIAN
            # ----------------------------------------------------

            if "guardian" in student_data:

                guardian = student_data.get("guardian") or {}

                if not isinstance(guardian, dict):
                    return APIResponse.error(
                        "Guardian data must be an object."
                    )

                guardian_map = {
                    "guardian_name": "guardian_name",
                    "guardian_phone": "guardian_phone",
                    "guardian_cnic": "guardian_cnic",
                    "relation": "relation",
                }

                for source, target in guardian_map.items():

                    if source in guardian:
                        update_data[target] = (
                            self._clean_string(
                                guardian[source]
                            )
                        )

                if "name" in guardian:
                    update_data["guardian_name"] = (
                        self._clean_string(
                            guardian["name"]
                        )
                    )

                if "phone" in guardian:
                    update_data["guardian_phone"] = (
                        self._clean_string(
                            guardian["phone"]
                        )
                    )

                if "cnic" in guardian:
                    update_data["guardian_cnic"] = (
                        self._clean_string(
                            guardian["cnic"]
                        )
                    )

            # ----------------------------------------------------
            # ALLOCATION
            # ----------------------------------------------------

            allocation_changed = False
            old_room_id = existing_student.get(
                "room_firebase_id"
            )

            new_room_id = old_room_id

            if "allocation" in student_data:

                allocation = student_data.get("allocation") or {}

                if not isinstance(allocation, dict):
                    return APIResponse.error(
                        "Allocation data must be an object."
                    )

                allocation_fields = {
                    "block": "block",
                    "room_type": "room_type",
                    "room_number": "room_number",
                    "room_firebase_id": "room_firebase_id",
                    "floor": "floor",
                    "bed_number": "bed_number",
                    "joining_date": "joining_date",
                    "remarks": "remarks",
                    "monthly_fee": "monthly_fee",
                    "security_deposit": "security_deposit",
                }

                for source, target in allocation_fields.items():

                    alternate = None

                    if source == "room_type":
                        alternate = "roomType"

                    elif source == "room_number":
                        alternate = "roomNumber"

                    elif source == "room_firebase_id":
                        alternate = "roomFirebaseId"

                    elif source == "bed_number":
                        alternate = "bedNumber"

                    elif source == "joining_date":
                        alternate = "joiningDate"

                    elif source == "monthly_fee":
                        alternate = "monthlyFee"

                    elif source == "security_deposit":
                        alternate = "securityDeposit"

                    if source in allocation:

                        value = allocation[source]

                    elif alternate and alternate in allocation:

                        value = allocation[alternate]

                    else:

                        continue

                    allocation_changed = True

                    if source in {
                        "block",
                    }:
                        value = self._clean_upper(value)

                    elif source in {
                        "room_number",
                        "bed_number",
                    }:
                        value = self._clean_upper(value)

                    elif source in {
                        "room_type",
                        "joining_date",
                        "remarks",
                    }:
                        value = self._clean_string(value)

                    elif source == "room_firebase_id":
                        value = self._clean_string(value)

                    elif source == "monthly_fee":
                        value = self._normalize_money(
                            value,
                            "Monthly fee",
                            allow_zero=True,
                        )

                    elif source == "security_deposit":
                        value = self._normalize_money(
                            value,
                            "Security deposit",
                            allow_zero=True,
                        )

                    update_data[target] = value

                if "floor" in allocation:

                    floor = allocation["floor"]

                    if floor is not None:

                        try:
                            floor = int(floor)
                        except (TypeError, ValueError):

                            return APIResponse.error(
                                "Floor must be a valid number."
                            )

                        if floor < 0:

                            return APIResponse.error(
                                "Floor cannot be negative."
                            )

                    update_data["floor"] = floor

                new_room_id = update_data.get(
                    "room_firebase_id",
                    old_room_id,
                )

            # ----------------------------------------------------
            # STATUS
            # ----------------------------------------------------

            if "status" in student_data:

                status = self._enum_value(
                    student_data.get("status")
                )

                if status not in {
                    "Active",
                    "Inactive",
                }:

                    return APIResponse.error(
                        "Invalid student status."
                    )

                update_data["status"] = status

            # ----------------------------------------------------
            # VALIDATE UPDATE
            # ----------------------------------------------------

            if not update_data:

                return APIResponse.error(
                    "No data provided for update."
                )

            # Required fields cannot become empty.
            protected_fields = {
                "name": "Student name cannot be empty.",
                "cnic": "CNIC cannot be empty.",
                "phone": "Phone number cannot be empty.",
                "address": "Address cannot be empty.",
                "guardian_name": "Guardian name cannot be empty.",
                "guardian_phone": "Guardian phone cannot be empty.",
                "guardian_cnic": "Guardian CNIC cannot be empty.",
            }

            for field, message in protected_fields.items():

                if field in update_data:

                    if not self._clean_string(
                        update_data[field]
                    ):

                        return APIResponse.error(message)

            # ----------------------------------------------------
            # UNIQUE VALIDATION
            # ----------------------------------------------------

            self._check_unique_fields(
                update_data,
                existing_student,
            )

            # ----------------------------------------------------
            # ROOM CHANGE
            # ----------------------------------------------------

            room_changed = (
                new_room_id != old_room_id
            )

            if room_changed:

                if new_room_id:

                    allocation_for_validation = {
                        "room_firebase_id": new_room_id,
                        "room_number": update_data.get(
                            "room_number",
                            existing_student.get("room_number"),
                        ),
                        "floor": update_data.get(
                            "floor",
                            existing_student.get("floor"),
                        ),
                    }

                    self._validate_room_allocation(
                        allocation_for_validation
                    )

                # ------------------------------------------------
                # CHANGE ROOM
                # ------------------------------------------------

                if old_room_id and new_room_id:

                    room_response = (
                        self.room_service
                        .change_student_room(
                            old_room_id,
                            new_room_id,
                            student_id,
                        )
                    )

                    if not room_response.get("success"):

                        return APIResponse.error(
                            room_response.get(
                                "message",
                                "Unable to change student room.",
                            )
                        )

                # ------------------------------------------------
                # ASSIGN NEW ROOM
                # ------------------------------------------------

                elif new_room_id:

                    room_response = (
                        self.room_service
                        .assign_student_to_room(
                            new_room_id,
                            student_id,
                        )
                    )

                    if not room_response.get("success"):

                        return APIResponse.error(
                            room_response.get(
                                "message",
                                "Unable to assign student to room.",
                            )
                        )

                # ------------------------------------------------
                # REMOVE OLD ROOM
                # ------------------------------------------------

                elif old_room_id:

                    room_response = (
                        self.room_service
                        .remove_student_from_room(
                            old_room_id,
                            student_id,
                        )
                    )

                    if not room_response.get("success"):

                        logger.error(
                            "Student room removal failed after "
                            "student requested room removal | "
                            f"Student ID: {student_id}"
                        )

                        return APIResponse.error(
                            room_response.get(
                                "message",
                                "Unable to remove student from room.",
                            )
                        )

            # ----------------------------------------------------
            # UPDATE STUDENT
            # ----------------------------------------------------

            updated = self.repository.update_student(
                student_id,
                update_data,
            )

            if not updated:

                # Rollback room change where possible.
                if room_changed:

                    try:

                        if old_room_id and new_room_id:

                            self.room_service.change_student_room(
                                new_room_id,
                                old_room_id,
                                student_id,
                            )

                        elif new_room_id and not old_room_id:

                            self.room_service.remove_student_from_room(
                                new_room_id,
                                student_id,
                            )

                        elif old_room_id and not new_room_id:

                            self.room_service.assign_student_to_room(
                                old_room_id,
                                student_id,
                            )

                    except Exception:

                        logger.exception(
                            "Room rollback failed after "
                            "student update failure."
                        )

                return APIResponse.error(
                    "Student update failed."
                )

            # ----------------------------------------------------
            # FETCH UPDATED STUDENT
            # ----------------------------------------------------

            updated_student = (
                self.repository
                .get_student_by_student_id(student_id)
            )

            if not updated_student:

                return APIResponse.error(
                    "Student not found after update."
                )

            logger.info(
                "Student updated successfully | "
                f"Student ID: {student_id}"
            )

            return APIResponse.success(
                "Student updated successfully.",
                self._serialize_student(
                    updated_student
                ),
            )

        except ValueError as exc:

            logger.warning(
                f"Student update validation failed | {exc}"
            )

            return APIResponse.error(str(exc))

        except Exception as exc:

            logger.exception(
                "Failed to update student."
            )

            return APIResponse.error(
                "Unable to update student.",
                str(exc),
            )

    # ============================================================
    # DELETE / DISABLE
    # ============================================================

    def delete_student(self, student_id: str):

        try:

            student_id = self._clean_upper(student_id)

            if not student_id:

                return APIResponse.error(
                    "Student ID is required."
                )

            student = (
                self.repository
                .get_student_by_student_id(student_id)
            )

            if not student:

                return APIResponse.error(
                    "Student not found."
                )

            room_id = student.get(
                "room_firebase_id"
            )

            # Remove student from room first.
            if room_id:

                room_response = (
                    self.room_service
                    .remove_student_from_room(
                        room_id,
                        student_id,
                    )
                )

                if not room_response.get("success"):

                    return APIResponse.error(
                        room_response.get(
                            "message",
                            "Unable to remove student from room.",
                        )
                    )

            deleted = (
                self.repository
                .disable_student(student_id)
            )

            if not deleted:

                # Try to restore room allocation.
                if room_id:

                    try:
                        self.room_service.assign_student_to_room(
                            room_id,
                            student_id,
                        )
                    except Exception:
                        logger.exception(
                            "Failed to restore room after "
                            "student disable failure."
                        )

                return APIResponse.error(
                    "Student deletion failed."
                )

            logger.info(
                "Student disabled successfully | "
                f"Student ID: {student_id}"
            )

            return APIResponse.success(
                "Student disabled successfully.",
                {
                    "student_id": student_id,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to disable student."
            )

            return APIResponse.error(
                "Unable to disable student.",
                str(exc),
            )

    # ============================================================
    # SEARCH
    # ============================================================

    def search_students(self, keyword: str):

        try:

            keyword = self._clean_string(keyword)

            if not keyword:

                return APIResponse.error(
                    "Search keyword is required."
                )

            students = (
                self.repository
                .search_students(keyword)
            )

            serialized = [
                self._serialize_student(student)
                for student in students
            ]

            logger.info(
                "Student search completed | "
                f"Keyword: {keyword} | "
                f"Results: {len(serialized)}"
            )

            return APIResponse.success(
                "Students retrieved successfully.",
                {
                    "total_students": len(serialized),
                    "students": serialized,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to search students."
            )

            return APIResponse.error(
                "Unable to search students.",
                str(exc),
            )

    # ============================================================
    # COUNT
    # ============================================================

    def count_students(self):

        try:

            total_students = (
                self.repository.count_students()
            )

            return APIResponse.success(
                "Student count retrieved successfully.",
                {
                    "total_students": total_students,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to count students."
            )

            return APIResponse.error(
                "Unable to count students.",
                str(exc),
            )

    # ============================================================
    # ACTIVE STUDENTS
    # ============================================================

    def get_active_students(self):

        try:

            students = (
                self.repository
                .get_active_students()
            )

            serialized = [
                self._serialize_student(student)
                for student in students
            ]

            return APIResponse.success(
                "Active students retrieved successfully.",
                {
                    "total_students": len(serialized),
                    "students": serialized,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve active students."
            )

            return APIResponse.error(
                "Unable to retrieve active students.",
                str(exc),
            )

    # ============================================================
    # INACTIVE STUDENTS
    # ============================================================

    def get_inactive_students(self):

        try:

            students = (
                self.repository
                .get_inactive_students()
            )

            serialized = [
                self._serialize_student(student)
                for student in students
            ]

            return APIResponse.success(
                "Inactive students retrieved successfully.",
                {
                    "total_students": len(serialized),
                    "students": serialized,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve inactive students."
            )

            return APIResponse.error(
                "Unable to retrieve inactive students.",
                str(exc),
            )

    # ============================================================
    # STUDENTS BY ROOM
    # ============================================================

    def get_students_by_room(
        self,
        room_firebase_id: str,
    ):

        try:

            room_firebase_id = (
                self._clean_string(
                    room_firebase_id
                )
            )

            if not room_firebase_id:

                return APIResponse.error(
                    "Room ID is required."
                )

            students = (
                self.repository
                .get_students_by_room(
                    room_firebase_id
                )
            )

            serialized = [
                self._serialize_student(student)
                for student in students
            ]

            return APIResponse.success(
                "Room students retrieved successfully.",
                {
                    "total_students": len(serialized),
                    "students": serialized,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve students by room."
            )

            return APIResponse.error(
                "Unable to retrieve students by room.",
                str(exc),
            )

    # ============================================================
    # STUDENTS WITHOUT ROOM
    # ============================================================

    def get_students_without_room(self):

        try:

            students = (
                self.repository
                .get_students_without_room()
            )

            serialized = [
                self._serialize_student(student)
                for student in students
            ]

            return APIResponse.success(
                "Students without room retrieved successfully.",
                {
                    "total_students": len(serialized),
                    "students": serialized,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve students without room."
            )

            return APIResponse.error(
                "Unable to retrieve students without room.",
                str(exc),
            )

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_student_statistics(self):

        try:

            statistics = (
                self.repository
                .get_student_statistics()
            )

            return APIResponse.success(
                "Student statistics retrieved successfully.",
                statistics,
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve student statistics."
            )

            return APIResponse.error(
                "Unable to retrieve student statistics.",
                str(exc),
            )