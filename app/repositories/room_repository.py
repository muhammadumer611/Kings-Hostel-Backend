from datetime import UTC, datetime
from typing import Optional

from firebase_admin import firestore

from app.firebase.firebase import db
from app.utils.logger import logger


class RoomRepository:

    def __init__(self):
        self.collection = db.collection("rooms")

    # ============================================================
    # PRIVATE HELPERS
    # ============================================================

    @staticmethod
    def _get_timestamp() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _normalize_room_number(room_number: str) -> str:
        return str(room_number or "").strip().upper()

    @staticmethod
    def _normalize_student_id(student_id: str) -> str:
        return str(student_id or "").strip()

    @staticmethod
    def _clean_student_ids(student_ids) -> list[str]:
        if not student_ids:
            return []

        cleaned = []
        seen = set()

        for student_id in student_ids:
            normalized = str(student_id or "").strip()

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            cleaned.append(normalized)

        return cleaned

    @staticmethod
    def _calculate_metrics(
        total_beds: int,
        occupied_beds: int,
    ) -> tuple[int, int, str]:

        total_beds = max(int(total_beds or 0), 0)
        occupied_beds = max(int(occupied_beds or 0), 0)

        occupied_beds = min(
            occupied_beds,
            total_beds,
        )

        available_beds = total_beds - occupied_beds

        if occupied_beds == 0:
            status = "Available"

        elif occupied_beds >= total_beds:
            status = "Occupied"

        else:
            status = "Partially Occupied"

        return (
            occupied_beds,
            available_beds,
            status,
        )

    def _normalize_room_data(
        self,
        room_data: dict,
    ) -> dict:

        normalized = dict(room_data or {})

        if "room_number" in normalized:
            normalized["room_number"] = self._normalize_room_number(
                normalized.get("room_number")
            )

        if "floor" in normalized:
            normalized["floor"] = int(normalized["floor"])

        if "total_beds" in normalized:
            normalized["total_beds"] = int(normalized["total_beds"])

        if "monthly_fee" in normalized:
            normalized["monthly_fee"] = float(
                normalized["monthly_fee"]
            )

        if "security_deposit" in normalized:
            normalized["security_deposit"] = float(
                normalized["security_deposit"]
            )

        if "is_active" in normalized:
            normalized["is_active"] = bool(
                normalized["is_active"]
            )

        if "current_students" in normalized:
            normalized["current_students"] = (
                self._clean_student_ids(
                    normalized.get("current_students")
                )
            )

        return normalized

    @staticmethod
    def _sort_rooms(rooms: list[dict]) -> list[dict]:

        return sorted(
            rooms,
            key=lambda item: (
                int(item.get("floor") or 0),
                str(
                    item.get("room_number") or ""
                ).upper(),
            ),
        )

    def _prepare_room_response(
        self,
        firebase_id: str,
        data: dict,
    ) -> dict:

        normalized = dict(data or {})

        normalized["firebase_id"] = firebase_id

        total_beds = int(
            normalized.get("total_beds") or 0
        )

        students = self._clean_student_ids(
            normalized.get("current_students")
        )

        occupied_beds, available_beds, status = (
            self._calculate_metrics(
                total_beds,
                len(students),
            )
        )

        normalized["current_students"] = students
        normalized["occupied_beds"] = occupied_beds
        normalized["available_beds"] = available_beds
        normalized["status"] = status

        return normalized

    # ============================================================
    # CREATE ROOM
    # ============================================================

    def create_room(
        self,
        room_data: dict,
    ) -> str:

        try:
            normalized = self._normalize_room_data(
                room_data
            )

            room_number = normalized.get(
                "room_number"
            )

            if not room_number:
                raise ValueError(
                    "Room number cannot be empty."
                )

            floor = normalized.get("floor")

            if floor is None:
                raise ValueError(
                    "Floor is required."
                )

            if floor < 0:
                raise ValueError(
                    "Floor cannot be negative."
                )

            total_beds = int(
                normalized.get("total_beds", 0)
            )

            if total_beds <= 0:
                raise ValueError(
                    "Total beds must be greater than 0."
                )

            monthly_fee = float(
                normalized.get("monthly_fee", 0)
            )

            if monthly_fee <= 0:
                raise ValueError(
                    "Monthly fee must be greater than 0."
                )

            security_deposit = float(
                normalized.get("security_deposit", 0)
            )

            if security_deposit < 0:
                raise ValueError(
                    "Security deposit cannot be negative."
                )

            # Check duplicate against ACTIVE + INACTIVE rooms.
            existing_room = self.get_room_by_number(
                room_number,
                include_inactive=True,
            )

            if existing_room:
                raise ValueError(
                    f"Room number '{room_number}' already exists."
                )

            timestamp = self._get_timestamp()

            room_ref = self.collection.document()

            room_document = {
                "room_number": room_number,
                "floor": floor,
                "total_beds": total_beds,
                "occupied_beds": 0,
                "available_beds": total_beds,
                "status": "Available",
                "monthly_fee": monthly_fee,
                "security_deposit": security_deposit,
                "is_active": True,
                "current_students": [],
                "created_at": timestamp,
                "updated_at": timestamp,
            }

            room_ref.set(room_document)

            logger.info(
                f"Room created successfully | "
                f"ID: {room_ref.id} | "
                f"Room: {room_number}"
            )

            return room_ref.id

        except Exception:
            logger.exception(
                "Failed to create room."
            )
            raise

    # ============================================================
    # GET ALL ACTIVE ROOMS
    # ============================================================

    def get_all_rooms(self) -> list[dict]:

        try:
            rooms = (
                self.collection
                .where("is_active", "==", True)
                .stream()
            )

            room_list = []

            for room in rooms:
                data = room.to_dict() or {}

                room_data = self._prepare_room_response(
                    room.id,
                    data,
                )

                room_list.append(room_data)

            room_list = self._sort_rooms(
                room_list
            )

            logger.info(
                f"Rooms retrieved successfully | "
                f"Total: {len(room_list)}"
            )

            return room_list

        except Exception:
            logger.exception(
                "Failed to retrieve rooms."
            )
            raise

    # ============================================================
    # GET ROOM BY ID
    # ============================================================

    def get_room_by_id(
        self,
        firebase_id: str,
        include_inactive: bool = False,
    ) -> Optional[dict]:

        try:
            firebase_id = str(
                firebase_id or ""
            ).strip()

            if not firebase_id:
                return None

            room_ref = self.collection.document(
                firebase_id
            )

            room_doc = room_ref.get()

            if not room_doc.exists:
                return None

            data = room_doc.to_dict() or {}

            if (
                not include_inactive
                and not data.get("is_active", True)
            ):
                return None

            return self._prepare_room_response(
                room_doc.id,
                data,
            )

        except Exception:
            logger.exception(
                "Failed to retrieve room by ID."
            )
            raise

    # ============================================================
    # GET ROOM BY ROOM NUMBER
    # ============================================================

    def get_room_by_number(
        self,
        room_number: str,
        include_inactive: bool = False,
    ) -> Optional[dict]:

        try:
            normalized_number = (
                self._normalize_room_number(
                    room_number
                )
            )

            if not normalized_number:
                return None

            query = (
                self.collection
                .where(
                    "room_number",
                    "==",
                    normalized_number,
                )
                .limit(10)
            )

            for room in query.stream():

                data = room.to_dict() or {}

                if (
                    not include_inactive
                    and not data.get(
                        "is_active",
                        True,
                    )
                ):
                    continue

                return self._prepare_room_response(
                    room.id,
                    data,
                )

            return None

        except Exception:
            logger.exception(
                "Failed to retrieve room by number."
            )
            raise

    # ============================================================
    # ROOM EXISTS
    # ============================================================

    def room_exists(
        self,
        firebase_id: str,
    ) -> bool:

        try:
            firebase_id = str(
                firebase_id or ""
            ).strip()

            if not firebase_id:
                return False

            room_doc = (
                self.collection
                .document(firebase_id)
                .get()
            )

            return room_doc.exists

        except Exception:
            logger.exception(
                "Failed to check room existence."
            )
            raise

    # ============================================================
    # COUNT ACTIVE ROOMS
    # ============================================================

    def count_rooms(self) -> int:

        try:
            total_rooms = sum(
                1
                for _ in (
                    self.collection
                    .where(
                        "is_active",
                        "==",
                        True,
                    )
                    .stream()
                )
            )

            logger.info(
                f"Room count retrieved successfully | "
                f"Total: {total_rooms}"
            )

            return total_rooms

        except Exception:
            logger.exception(
                "Failed to count rooms."
            )
            raise

    # ============================================================
    # UPDATE ROOM
    # ============================================================

    def update_room(
        self,
        firebase_id: str,
        room_data: dict,
    ) -> bool:

        try:
            room_ref = self.collection.document(
                firebase_id
            )

            room_doc = room_ref.get()

            if not room_doc.exists:
                return False

            existing_data = (
                room_doc.to_dict() or {}
            )

            if not existing_data.get(
                "is_active",
                True,
            ):
                raise ValueError(
                    "Cannot update an inactive room."
                )

            normalized_update = (
                self._normalize_room_data(
                    room_data
                )
            )

            if not normalized_update:
                return False

            # ----------------------------------------------------
            # ROOM NUMBER
            # ----------------------------------------------------

            if "room_number" in normalized_update:

                new_room_number = (
                    normalized_update[
                        "room_number"
                    ]
                )

                if not new_room_number:
                    raise ValueError(
                        "Room number cannot be empty."
                    )

                old_room_number = (
                    self._normalize_room_number(
                        existing_data.get(
                            "room_number"
                        )
                    )
                )

                if (
                    new_room_number
                    != old_room_number
                ):

                    duplicate_room = (
                        self.get_room_by_number(
                            new_room_number,
                            include_inactive=True,
                        )
                    )

                    if (
                        duplicate_room
                        and duplicate_room[
                            "firebase_id"
                        ] != firebase_id
                    ):
                        raise ValueError(
                            f"Room number "
                            f"'{new_room_number}' "
                            f"already exists."
                        )

            # ----------------------------------------------------
            # FLOOR
            # ----------------------------------------------------

            if "floor" in normalized_update:

                if normalized_update[
                    "floor"
                ] < 0:
                    raise ValueError(
                        "Floor cannot be negative."
                    )

            # ----------------------------------------------------
            # BEDS
            # ----------------------------------------------------

            current_students = (
                self._clean_student_ids(
                    existing_data.get(
                        "current_students"
                    )
                )
            )

            occupied_beds = len(
                current_students
            )

            if "total_beds" in normalized_update:

                new_total_beds = int(
                    normalized_update[
                        "total_beds"
                    ]
                )

                if new_total_beds <= 0:
                    raise ValueError(
                        "Total beds must be greater than 0."
                    )

                if new_total_beds < occupied_beds:
                    raise ValueError(
                        "Total beds cannot be "
                        "less than current occupied beds."
                    )

            total_beds = int(
                normalized_update.get(
                    "total_beds",
                    existing_data.get(
                        "total_beds",
                        0,
                    ),
                )
            )

            # ----------------------------------------------------
            # FEES
            # ----------------------------------------------------

            if "monthly_fee" in normalized_update:

                if normalized_update[
                    "monthly_fee"
                ] <= 0:
                    raise ValueError(
                        "Monthly fee must be greater than 0."
                    )

            if "security_deposit" in normalized_update:

                if normalized_update[
                    "security_deposit"
                ] < 0:
                    raise ValueError(
                        "Security deposit cannot be negative."
                    )

            # ----------------------------------------------------
            # NEVER TRUST CLIENT OCCUPANCY VALUES
            # ----------------------------------------------------

            occupied_beds, available_beds, status = (
                self._calculate_metrics(
                    total_beds,
                    occupied_beds,
                )
            )

            normalized_update[
                "current_students"
            ] = current_students

            normalized_update[
                "occupied_beds"
            ] = occupied_beds

            normalized_update[
                "available_beds"
            ] = available_beds

            normalized_update[
                "status"
            ] = status

            normalized_update[
                "updated_at"
            ] = self._get_timestamp()

            room_ref.update(
                normalized_update
            )

            logger.info(
                f"Room updated successfully | "
                f"ID: {firebase_id}"
            )

            return True

        except Exception:
            logger.exception(
                "Failed to update room."
            )
            raise

    # ============================================================
    # SOFT DELETE ROOM
    # ============================================================

    def delete_room(
        self,
        firebase_id: str,
    ) -> bool:

        try:
            room_ref = self.collection.document(
                firebase_id
            )

            room_doc = room_ref.get()

            if not room_doc.exists:
                return False

            room_data = (
                room_doc.to_dict() or {}
            )

            students = self._clean_student_ids(
                room_data.get(
                    "current_students"
                )
            )

            if students:
                raise ValueError(
                    "Cannot delete room because "
                    "students are currently living in it."
                )

            if not room_data.get(
                "is_active",
                True,
            ):
                return False

            room_ref.update(
                {
                    "is_active": False,
                    "status": "Available",
                    "occupied_beds": 0,
                    "available_beds": int(
                        room_data.get(
                            "total_beds",
                            0,
                        )
                    ),
                    "current_students": [],
                    "updated_at": self._get_timestamp(),
                }
            )

            logger.info(
                f"Room disabled successfully | "
                f"ID: {firebase_id}"
            )

            return True

        except Exception:
            logger.exception(
                "Failed to delete room."
            )
            raise

    # ============================================================
    # SEARCH ROOMS
    # ============================================================

    def search_rooms(
        self,
        keyword: str,
    ) -> list[dict]:

        try:
            keyword = str(
                keyword or ""
            ).strip().lower()

            if not keyword:
                return []

            rooms = (
                self.collection
                .where(
                    "is_active",
                    "==",
                    True,
                )
                .stream()
            )

            result = []

            for room in rooms:

                data = room.to_dict() or {}

                room_data = (
                    self._prepare_room_response(
                        room.id,
                        data,
                    )
                )

                room_number = str(
                    room_data.get(
                        "room_number",
                        "",
                    )
                ).lower()

                floor = str(
                    room_data.get(
                        "floor",
                        "",
                    )
                ).lower()

                status = str(
                    room_data.get(
                        "status",
                        "",
                    )
                ).lower()

                monthly_fee = str(
                    room_data.get(
                        "monthly_fee",
                        "",
                    )
                ).lower()

                if (
                    keyword in room_number
                    or keyword in floor
                    or keyword in status
                    or keyword in monthly_fee
                ):
                    result.append(
                        room_data
                    )

            result = self._sort_rooms(
                result
            )

            logger.info(
                f"Room search completed | "
                f"Keyword: {keyword} | "
                f"Results: {len(result)}"
            )

            return result

        except Exception:
            logger.exception(
                "Failed to search rooms."
            )
            raise

    # ============================================================
    # AVAILABLE ROOMS
    # ============================================================

    def get_available_rooms(self) -> list[dict]:

        try:
            rooms = self.get_all_rooms()

            result = [
                room
                for room in rooms
                if int(
                    room.get(
                        "available_beds",
                        0,
                    )
                ) > 0
            ]

            logger.info(
                f"Available rooms retrieved | "
                f"Total: {len(result)}"
            )

            return result

        except Exception:
            logger.exception(
                "Failed to retrieve available rooms."
            )
            raise

    # ============================================================
    # OCCUPIED ROOMS
    # ============================================================

    def get_occupied_rooms(self) -> list[dict]:

        try:
            rooms = self.get_all_rooms()

            result = [
                room
                for room in rooms
                if int(
                    room.get(
                        "occupied_beds",
                        0,
                    )
                ) > 0
            ]

            logger.info(
                f"Occupied rooms retrieved | "
                f"Total: {len(result)}"
            )

            return result

        except Exception:
            logger.exception(
                "Failed to retrieve occupied rooms."
            )
            raise

    # ============================================================
    # ASSIGN STUDENT TO ROOM
    # ============================================================

    def assign_student_to_room(
        self,
        firebase_id: str,
        student_id: str,
    ) -> bool:

        student_id = (
            self._normalize_student_id(
                student_id
            )
        )

        if not student_id:
            raise ValueError(
                "Student ID cannot be empty."
            )

        @firestore.transactional
        def _assign(transaction):

            room_ref = (
                self.collection.document(
                    firebase_id
                )
            )

            room_doc = room_ref.get(
                transaction=transaction
            )

            if not room_doc.exists:
                return False

            data = (
                room_doc.to_dict() or {}
            )

            if not data.get(
                "is_active",
                True,
            ):
                raise ValueError(
                    "Room is disabled."
                )

            students = self._clean_student_ids(
                data.get(
                    "current_students"
                )
            )

            if student_id in students:
                raise ValueError(
                    "Student is already assigned "
                    "to this room."
                )

            total_beds = int(
                data.get(
                    "total_beds",
                    0,
                )
            )

            if len(students) >= total_beds:
                raise ValueError(
                    "Room is already full."
                )

            students.append(
                student_id
            )

            occupied_beds, available_beds, status = (
                self._calculate_metrics(
                    total_beds,
                    len(students),
                )
            )

            transaction.update(
                room_ref,
                {
                    "current_students": students,
                    "occupied_beds": occupied_beds,
                    "available_beds": available_beds,
                    "status": status,
                    "updated_at": self._get_timestamp(),
                }
            )

            return True

        return _assign()

    # ============================================================
    # REMOVE STUDENT FROM ROOM
    # ============================================================

    def remove_student_from_room(
        self,
        firebase_id: str,
        student_id: str,
    ) -> bool:

        student_id = (
            self._normalize_student_id(
                student_id
            )
        )

        if not student_id:
            raise ValueError(
                "Student ID cannot be empty."
            )

        @firestore.transactional
        def _remove(transaction):

            room_ref = (
                self.collection.document(
                    firebase_id
                )
            )

            room_doc = room_ref.get(
                transaction=transaction
            )

            if not room_doc.exists:
                return False

            data = (
                room_doc.to_dict() or {}
            )

            students = self._clean_student_ids(
                data.get(
                    "current_students"
                )
            )

            if student_id not in students:
                return False

            students.remove(
                student_id
            )

            total_beds = int(
                data.get(
                    "total_beds",
                    0,
                )
            )

            occupied_beds, available_beds, status = (
                self._calculate_metrics(
                    total_beds,
                    len(students),
                )
            )

            transaction.update(
                room_ref,
                {
                    "current_students": students,
                    "occupied_beds": occupied_beds,
                    "available_beds": available_beds,
                    "status": status,
                    "updated_at": self._get_timestamp(),
                }
            )

            return True

        return _remove()

    # ============================================================
    # CHANGE STUDENT ROOM
    # ============================================================

    def change_student_room(
        self,
        from_room_id: str,
        to_room_id: str,
        student_id: str,
    ) -> bool:

        student_id = (
            self._normalize_student_id(
                student_id
            )
        )

        if not student_id:
            raise ValueError(
                "Student ID cannot be empty."
            )

        if from_room_id == to_room_id:
            raise ValueError(
                "Source and destination rooms "
                "cannot be the same."
            )

        @firestore.transactional
        def _change(transaction):

            from_ref = (
                self.collection.document(
                    from_room_id
                )
            )

            to_ref = (
                self.collection.document(
                    to_room_id
                )
            )

            from_doc = from_ref.get(
                transaction=transaction
            )

            to_doc = to_ref.get(
                transaction=transaction
            )

            if (
                not from_doc.exists
                or not to_doc.exists
            ):
                return False

            from_data = (
                from_doc.to_dict() or {}
            )

            to_data = (
                to_doc.to_dict() or {}
            )

            if not from_data.get(
                "is_active",
                True,
            ):
                raise ValueError(
                    "Source room is disabled."
                )

            if not to_data.get(
                "is_active",
                True,
            ):
                raise ValueError(
                    "Destination room is disabled."
                )

            from_students = (
                self._clean_student_ids(
                    from_data.get(
                        "current_students"
                    )
                )
            )

            to_students = (
                self._clean_student_ids(
                    to_data.get(
                        "current_students"
                    )
                )
            )

            if student_id not in from_students:
                raise ValueError(
                    "Student is not assigned "
                    "to the source room."
                )

            if student_id in to_students:
                raise ValueError(
                    "Student is already assigned "
                    "to the destination room."
                )

            to_total_beds = int(
                to_data.get(
                    "total_beds",
                    0,
                )
            )

            if len(to_students) >= to_total_beds:
                raise ValueError(
                    "Destination room is already full."
                )

            from_students.remove(
                student_id
            )

            to_students.append(
                student_id
            )

            from_total_beds = int(
                from_data.get(
                    "total_beds",
                    0,
                )
            )

            (
                from_occupied,
                from_available,
                from_status,
            ) = self._calculate_metrics(
                from_total_beds,
                len(from_students),
            )

            (
                to_occupied,
                to_available,
                to_status,
            ) = self._calculate_metrics(
                to_total_beds,
                len(to_students),
            )

            timestamp = self._get_timestamp()

            transaction.update(
                from_ref,
                {
                    "current_students": from_students,
                    "occupied_beds": from_occupied,
                    "available_beds": from_available,
                    "status": from_status,
                    "updated_at": timestamp,
                }
            )

            transaction.update(
                to_ref,
                {
                    "current_students": to_students,
                    "occupied_beds": to_occupied,
                    "available_beds": to_available,
                    "status": to_status,
                    "updated_at": timestamp,
                }
            )

            return True

        return _change()

    # ============================================================
    # DISABLE ROOM
    # ============================================================

    def disable_room(
        self,
        firebase_id: str,
    ) -> bool:

        try:
            room_ref = self.collection.document(
                firebase_id
            )

            room_doc = room_ref.get()

            if not room_doc.exists:
                return False

            data = (
                room_doc.to_dict() or {}
            )

            students = self._clean_student_ids(
                data.get(
                    "current_students"
                )
            )

            if students:
                raise ValueError(
                    "Cannot disable room because "
                    "students are currently living in it."
                )

            if not data.get(
                "is_active",
                True,
            ):
                return False

            room_ref.update(
                {
                    "is_active": False,
                    "updated_at": self._get_timestamp(),
                }
            )

            logger.info(
                f"Room disabled successfully | "
                f"ID: {firebase_id}"
            )

            return True

        except Exception:
            logger.exception(
                "Failed to disable room."
            )
            raise

    # ============================================================
    # ENABLE ROOM
    # ============================================================

    def enable_room(
        self,
        firebase_id: str,
    ) -> bool:

        try:
            room_ref = self.collection.document(
                firebase_id
            )

            room_doc = room_ref.get()

            if not room_doc.exists:
                return False

            data = (
                room_doc.to_dict() or {}
            )

            if data.get(
                "is_active",
                True,
            ):
                return False

            students = self._clean_student_ids(
                data.get(
                    "current_students"
                )
            )

            total_beds = int(
                data.get(
                    "total_beds",
                    0,
                )
            )

            if total_beds <= 0:
                raise ValueError(
                    "Room has invalid bed capacity."
                )

            if len(students) > total_beds:
                raise ValueError(
                    "Room cannot be enabled because "
                    "occupied beds exceed total beds."
                )

            occupied_beds, available_beds, status = (
                self._calculate_metrics(
                    total_beds,
                    len(students),
                )
            )

            room_ref.update(
                {
                    "is_active": True,
                    "current_students": students,
                    "occupied_beds": occupied_beds,
                    "available_beds": available_beds,
                    "status": status,
                    "updated_at": self._get_timestamp(),
                }
            )

            logger.info(
                f"Room enabled successfully | "
                f"ID: {firebase_id}"
            )

            return True

        except Exception:
            logger.exception(
                "Failed to enable room."
            )
            raise

    # ============================================================
    # ROOMS WITH AVAILABLE BEDS
    # ============================================================

    def get_rooms_with_available_beds(
        self,
    ) -> list[dict]:

        try:
            return self.get_available_rooms()

        except Exception:
            logger.exception(
                "Failed to retrieve rooms "
                "with available beds."
            )
            raise

    # ============================================================
    # ROOM STATISTICS
    # ============================================================

    def get_room_statistics(self) -> dict:

        try:
            rooms = self.get_all_rooms()

            total_rooms = len(rooms)

            available_rooms = sum(
                1
                for room in rooms
                if room.get("status")
                == "Available"
            )

            partially_occupied_rooms = sum(
                1
                for room in rooms
                if room.get("status")
                == "Partially Occupied"
            )

            occupied_rooms = sum(
                1
                for room in rooms
                if room.get("status")
                == "Occupied"
            )

            total_beds = sum(
                int(
                    room.get(
                        "total_beds",
                        0,
                    )
                )
                for room in rooms
            )

            occupied_beds = sum(
                int(
                    room.get(
                        "occupied_beds",
                        0,
                    )
                )
                for room in rooms
            )

            available_beds = sum(
                int(
                    room.get(
                        "available_beds",
                        0,
                    )
                )
                for room in rooms
            )

            occupancy_rate = (
                round(
                    (
                        occupied_beds
                        / total_beds
                    )
                    * 100,
                    2,
                )
                if total_beds > 0
                else 0.0
            )

            stats = {
                "total_rooms": total_rooms,
                "available_rooms": available_rooms,
                "partially_occupied_rooms": (
                    partially_occupied_rooms
                ),
                "occupied_rooms": occupied_rooms,
                "total_beds": total_beds,
                "occupied_beds": occupied_beds,
                "available_beds": available_beds,
                "occupancy_rate": occupancy_rate,
            }

            logger.info(
                f"Room statistics generated | "
                f"{stats}"
            )

            return stats

        except Exception:
            logger.exception(
                "Failed to generate room statistics."
            )
            raise