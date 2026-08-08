from datetime import datetime

from app.repositories.room_repository import RoomRepository
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class RoomService:

    def __init__(self):
        self.repository = RoomRepository()

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================

    def _format_timestamp(self, value):
        """
        Convert Firestore/Python datetime values into ISO strings.
        """
        if isinstance(value, datetime):
            return value.isoformat()

        if not value:
            return None

        return str(value)

    def _calculate_status(
        self,
        occupied_beds: int,
        total_beds: int,
    ) -> str:
        """
        Calculate room occupancy status.
        """

        total_beds = max(int(total_beds or 0), 0)
        occupied_beds = max(int(occupied_beds or 0), 0)

        if occupied_beds > total_beds:
            occupied_beds = total_beds

        if occupied_beds == 0:
            return "Available"

        if occupied_beds >= total_beds:
            return "Occupied"

        return "Partially Occupied"

    def _calculate_room_metrics(self, room: dict):
        """
        Calculate occupied beds, available beds and status.
        """

        total_beds = max(
            int(room.get("total_beds", 0) or 0),
            0,
        )

        occupied_beds = max(
            int(room.get("occupied_beds", 0) or 0),
            0,
        )

        if occupied_beds > total_beds:
            occupied_beds = total_beds

        available_beds = max(
            total_beds - occupied_beds,
            0,
        )

        status = self._calculate_status(
            occupied_beds,
            total_beds,
        )

        return (
            occupied_beds,
            available_beds,
            status,
        )

    def _serialize_room(self, room: dict):
        """
        Convert repository room data into frontend-safe response data.
        """

        if not room:
            return None

        occupied_beds, available_beds, status = (
            self._calculate_room_metrics(room)
        )

        current_students = [
            str(student).strip()
            for student in (room.get("current_students") or [])
            if str(student).strip()
        ]

        return {
            "firebase_id": room.get("firebase_id"),
            "room_number": str(
                room.get("room_number", "")
            ).strip().upper(),

            "floor": int(
                room.get("floor", 0) or 0
            ),

            "total_beds": int(
                room.get("total_beds", 0) or 0
            ),

            "occupied_beds": occupied_beds,

            "available_beds": available_beds,

            "status": status,

            "monthly_fee": float(
                room.get("monthly_fee", 0) or 0
            ),

            "security_deposit": float(
                room.get("security_deposit", 0) or 0
            ),

            "is_active": bool(
                room.get("is_active", True)
            ),

            "current_students": current_students,

            "created_at": self._format_timestamp(
                room.get("created_at")
            ),

            "updated_at": self._format_timestamp(
                room.get("updated_at")
            ),
        }

    def _serialize_room_list(self, rooms):
        """
        Serialize a list of rooms.
        """

        return [
            self._serialize_room(room)
            for room in (rooms or [])
        ]

    def _normalize_room_payload(
        self,
        room_data: dict,
        for_update: bool = False,
    ):
        """
        Validate and normalize room data before sending it
        to repository.
        """

        if not isinstance(room_data, dict):
            raise ValueError(
                "Room payload must be a dictionary."
            )

        normalized = {}

        # -------------------------
        # ROOM NUMBER
        # -------------------------

        if "room_number" in room_data:

            room_number = str(
                room_data.get("room_number", "")
            ).strip().upper()

            if not room_number:
                raise ValueError(
                    "Room number cannot be empty."
                )

            if len(room_number) > 20:
                raise ValueError(
                    "Room number cannot exceed 20 characters."
                )

            normalized["room_number"] = room_number

        # -------------------------
        # FLOOR
        # -------------------------

        if "floor" in room_data:

            floor = int(room_data["floor"])

            if floor < 0:
                raise ValueError(
                    "Floor cannot be negative."
                )

            normalized["floor"] = floor

        # -------------------------
        # TOTAL BEDS
        # -------------------------

        if "total_beds" in room_data:

            total_beds = int(
                room_data["total_beds"]
            )

            if total_beds < 1:
                raise ValueError(
                    "Total beds must be at least 1."
                )

            if total_beds > 20:
                raise ValueError(
                    "A room cannot have more than 20 beds."
                )

            normalized["total_beds"] = total_beds

        # -------------------------
        # MONTHLY FEE
        # -------------------------

        if "monthly_fee" in room_data:

            monthly_fee = float(
                room_data["monthly_fee"]
            )

            if monthly_fee <= 0:
                raise ValueError(
                    "Monthly fee must be greater than 0."
                )

            normalized["monthly_fee"] = monthly_fee

        # -------------------------
        # SECURITY DEPOSIT
        # -------------------------

        if "security_deposit" in room_data:

            security_deposit = float(
                room_data["security_deposit"]
            )

            if security_deposit < 0:
                raise ValueError(
                    "Security deposit cannot be negative."
                )

            normalized["security_deposit"] = (
                security_deposit
            )

        # -------------------------
        # ACTIVE STATUS
        # -------------------------

        if "is_active" in room_data:

            normalized["is_active"] = bool(
                room_data["is_active"]
            )

        # -------------------------
        # UPDATE VALIDATION
        # -------------------------

        if for_update and not normalized:
            raise ValueError(
                "No valid room fields were provided."
            )

        return normalized

    # =========================================================
    # CREATE ROOM
    # =========================================================

    def create_room(self, room_data: dict):

        try:

            normalized_room = (
                self._normalize_room_payload(
                    room_data
                )
            )

            room_number = normalized_room[
                "room_number"
            ]

            existing_room = (
                self.repository.get_room_by_number(
                    room_number
                )
            )

            if existing_room:
                return APIResponse.error(
                    "Room number already exists."
                )

            firebase_id = (
                self.repository.create_room(
                    normalized_room
                )
            )

            logger.info(
                f"Room created successfully | "
                f"Room: {room_number} | "
                f"ID: {firebase_id}"
            )

            return APIResponse.success(
                "Room created successfully.",
                {
                    "firebase_id": firebase_id
                },
            )

        except ValueError as exc:

            return APIResponse.error(
                str(exc)
            )

        except Exception as exc:

            logger.exception(
                "Failed to create room."
            )

            return APIResponse.error(
                "Unable to create room.",
                str(exc),
            )

    # =========================================================
    # GET ALL ROOMS
    # =========================================================

    def get_all_rooms(self):

        try:

            rooms = (
                self.repository.get_all_rooms()
            )

            serialized_rooms = (
                self._serialize_room_list(
                    rooms
                )
            )

            return APIResponse.success(
                "Rooms retrieved successfully.",
                {
                    "total_rooms": len(
                        serialized_rooms
                    ),
                    "rooms": serialized_rooms,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve rooms."
            )

            return APIResponse.error(
                "Unable to retrieve rooms.",
                str(exc),
            )

    # =========================================================
    # GET SINGLE ROOM
    # =========================================================

    def get_room_by_id(
        self,
        firebase_id: str,
    ):

        try:

            firebase_id = str(
                firebase_id or ""
            ).strip()

            if not firebase_id:
                return APIResponse.error(
                    "Room ID is required."
                )

            room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            if not room:

                logger.warning(
                    f"Room not found | ID: {firebase_id}"
                )

                return APIResponse.error(
                    "Room not found."
                )

            return APIResponse.success(
                "Room retrieved successfully.",
                self._serialize_room(room),
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve room."
            )

            return APIResponse.error(
                "Unable to retrieve room.",
                str(exc),
            )

    # =========================================================
    # UPDATE ROOM
    # =========================================================

    def update_room(
        self,
        firebase_id: str,
        room_data: dict,
    ):

        try:

            firebase_id = str(
                firebase_id or ""
            ).strip()

            if not firebase_id:
                return APIResponse.error(
                    "Room ID is required."
                )

            existing_room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            if not existing_room:

                return APIResponse.error(
                    "Room not found."
                )

            update_payload = (
                self._normalize_room_payload(
                    room_data,
                    for_update=True,
                )
            )

            # -------------------------
            # DUPLICATE ROOM NUMBER
            # -------------------------

            if "room_number" in update_payload:

                duplicate_room = (
                    self.repository.get_room_by_number(
                        update_payload[
                            "room_number"
                        ]
                    )
                )

                if (
                    duplicate_room
                    and duplicate_room.get(
                        "firebase_id"
                    ) != firebase_id
                ):

                    return APIResponse.error(
                        "Room number already exists."
                    )

            # -------------------------
            # TOTAL BEDS VALIDATION
            # -------------------------

            if "total_beds" in update_payload:

                occupied_beds = int(
                    existing_room.get(
                        "occupied_beds",
                        0,
                    )
                    or 0
                )

                if (
                    update_payload["total_beds"]
                    < occupied_beds
                ):

                    return APIResponse.error(
                        "Total beds cannot be less than current occupied beds."
                    )

            success = (
                self.repository.update_room(
                    firebase_id,
                    update_payload,
                )
            )

            if not success:

                return APIResponse.error(
                    "Unable to update room."
                )

            updated_room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            return APIResponse.success(
                "Room updated successfully.",
                self._serialize_room(
                    updated_room
                ),
            )

        except ValueError as exc:

            return APIResponse.error(
                str(exc)
            )

        except Exception as exc:

            logger.exception(
                "Failed to update room."
            )

            return APIResponse.error(
                "Unable to update room.",
                str(exc),
            )

    # =========================================================
    # DELETE ROOM
    # =========================================================

    def delete_room(
        self,
        firebase_id: str,
    ):

        try:

            room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            if not room:

                return APIResponse.error(
                    "Room not found."
                )

            if (
                room.get("current_students")
                or int(
                    room.get(
                        "occupied_beds",
                        0,
                    )
                    or 0
                )
                > 0
            ):

                return APIResponse.error(
                    "Cannot delete room because students are currently living in it."
                )

            success = (
                self.repository.delete_room(
                    firebase_id
                )
            )

            if not success:

                return APIResponse.error(
                    "Unable to delete room."
                )

            return APIResponse.success(
                "Room deleted successfully."
            )

        except ValueError as exc:

            return APIResponse.error(
                str(exc)
            )

        except Exception as exc:

            logger.exception(
                "Failed to delete room."
            )

            return APIResponse.error(
                "Unable to delete room.",
                str(exc),
            )

    # =========================================================
    # SEARCH ROOMS
    # =========================================================

    def search_rooms(
        self,
        keyword: str,
    ):

        try:

            keyword = str(
                keyword or ""
            ).strip()

            if not keyword:
                return APIResponse.error(
                    "Search keyword is required."
                )

            rooms = (
                self.repository.search_rooms(
                    keyword
                )
            )

            serialized_rooms = (
                self._serialize_room_list(
                    rooms
                )
            )

            return APIResponse.success(
                "Rooms retrieved successfully.",
                {
                    "total_rooms": len(
                        serialized_rooms
                    ),
                    "rooms": serialized_rooms,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to search rooms."
            )

            return APIResponse.error(
                "Unable to search rooms.",
                str(exc),
            )

    # =========================================================
    # ROOM COUNT
    # =========================================================

    def count_rooms(self):

        try:

            total_rooms = (
                self.repository.count_rooms()
            )

            return APIResponse.success(
                "Room count retrieved successfully.",
                {
                    "total_rooms": total_rooms
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to count rooms."
            )

            return APIResponse.error(
                "Unable to count rooms.",
                str(exc),
            )

    # =========================================================
    # AVAILABLE ROOMS
    # =========================================================

    def get_available_rooms(self):

        try:

            rooms = (
                self.repository.get_available_rooms()
            )

            serialized_rooms = (
                self._serialize_room_list(
                    rooms
                )
            )

            return APIResponse.success(
                "Available rooms retrieved successfully.",
                {
                    "total_rooms": len(
                        serialized_rooms
                    ),
                    "rooms": serialized_rooms,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve available rooms."
            )

            return APIResponse.error(
                "Unable to retrieve available rooms.",
                str(exc),
            )

    # =========================================================
    # ROOMS WITH AVAILABLE BEDS
    # =========================================================

    def get_rooms_with_available_beds(self):

        try:

            rooms = (
                self.repository
                .get_rooms_with_available_beds()
            )

            serialized_rooms = (
                self._serialize_room_list(
                    rooms
                )
            )

            return APIResponse.success(
                "Rooms with available beds retrieved successfully.",
                {
                    "total_rooms": len(
                        serialized_rooms
                    ),
                    "rooms": serialized_rooms,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve rooms with available beds."
            )

            return APIResponse.error(
                "Unable to retrieve rooms with available beds.",
                str(exc),
            )

    # =========================================================
    # OCCUPIED ROOMS
    # =========================================================

    def get_occupied_rooms(self):

        try:

            rooms = (
                self.repository.get_occupied_rooms()
            )

            serialized_rooms = (
                self._serialize_room_list(
                    rooms
                )
            )

            return APIResponse.success(
                "Occupied rooms retrieved successfully.",
                {
                    "total_rooms": len(
                        serialized_rooms
                    ),
                    "rooms": serialized_rooms,
                },
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve occupied rooms."
            )

            return APIResponse.error(
                "Unable to retrieve occupied rooms.",
                str(exc),
            )

    # =========================================================
    # ROOM ALLOCATION CHECK
    # =========================================================

    def get_room_for_allocation(
        self,
        firebase_id: str,
    ):

        try:

            room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            if not room:

                return APIResponse.error(
                    "Room not found."
                )

            if not room.get(
                "is_active",
                True,
            ):

                return APIResponse.error(
                    "Room is disabled."
                )

            available_beds = int(
                room.get(
                    "available_beds",
                    0,
                )
                or 0
            )

            if available_beds <= 0:

                return APIResponse.error(
                    "Room is already full."
                )

            return APIResponse.success(
                "Room is available for allocation.",
                self._serialize_room(room),
            )

        except Exception as exc:

            logger.exception(
                "Failed to fetch room for allocation."
            )

            return APIResponse.error(
                "Unable to fetch room for allocation.",
                str(exc),
            )

    # =========================================================
    # DISABLE ROOM
    # =========================================================

    def disable_room(
        self,
        firebase_id: str,
    ):

        try:

            room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            if not room:

                return APIResponse.error(
                    "Room not found."
                )

            if (
                room.get("current_students")
                or int(
                    room.get(
                        "occupied_beds",
                        0,
                    )
                    or 0
                )
                > 0
            ):

                return APIResponse.error(
                    "Cannot disable room because students are currently living in it."
                )

            success = (
                self.repository.disable_room(
                    firebase_id
                )
            )

            if not success:

                return APIResponse.error(
                    "Unable to disable room."
                )

            return APIResponse.success(
                "Room disabled successfully."
            )

        except ValueError as exc:

            return APIResponse.error(
                str(exc)
            )

        except Exception as exc:

            logger.exception(
                "Failed to disable room."
            )

            return APIResponse.error(
                "Unable to disable room.",
                str(exc),
            )

    # =========================================================
    # ENABLE ROOM
    # =========================================================

    def enable_room(
        self,
        firebase_id: str,
    ):

        try:

            room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            if not room:

                return APIResponse.error(
                    "Room not found."
                )

            success = (
                self.repository.enable_room(
                    firebase_id
                )
            )

            if not success:

                return APIResponse.error(
                    "Unable to enable room."
                )

            return APIResponse.success(
                "Room enabled successfully."
            )

        except Exception as exc:

            logger.exception(
                "Failed to enable room."
            )

            return APIResponse.error(
                "Unable to enable room.",
                str(exc),
            )

    # =========================================================
    # ASSIGN STUDENT TO ROOM
    # =========================================================

    def assign_student_to_room(
        self,
        firebase_id: str,
        student_id: str,
    ):

        try:

            firebase_id = str(
                firebase_id or ""
            ).strip()

            student_id = str(
                student_id or ""
            ).strip()

            if not firebase_id:
                return APIResponse.error(
                    "Room ID is required."
                )

            if not student_id:
                return APIResponse.error(
                    "Student ID is required."
                )

            room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            if not room:

                return APIResponse.error(
                    "Room not found."
                )

            if not room.get(
                "is_active",
                True,
            ):

                return APIResponse.error(
                    "Room is disabled."
                )

            current_students = [
                str(student).strip()
                for student in (
                    room.get(
                        "current_students"
                    )
                    or []
                )
                if str(student).strip()
            ]

            if student_id in current_students:

                return APIResponse.error(
                    "Student is already assigned to this room."
                )

            available_beds = int(
                room.get(
                    "available_beds",
                    0,
                )
                or 0
            )

            if available_beds <= 0:

                return APIResponse.error(
                    "Room is already full."
                )

            success = (
                self.repository.assign_student_to_room(
                    firebase_id,
                    student_id,
                )
            )

            if not success:

                return APIResponse.error(
                    "Unable to assign student to room."
                )

            updated_room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            return APIResponse.success(
                "Student assigned successfully.",
                self._serialize_room(
                    updated_room
                ),
            )

        except ValueError as exc:

            return APIResponse.error(
                str(exc)
            )

        except Exception as exc:

            logger.exception(
                "Failed to assign student to room."
            )

            return APIResponse.error(
                "Unable to assign student to room.",
                str(exc),
            )

    # =========================================================
    # REMOVE STUDENT FROM ROOM
    # =========================================================

    def remove_student_from_room(
        self,
        firebase_id: str,
        student_id: str,
    ):

        try:

            firebase_id = str(
                firebase_id or ""
            ).strip()

            student_id = str(
                student_id or ""
            ).strip()

            if not firebase_id:
                return APIResponse.error(
                    "Room ID is required."
                )

            if not student_id:
                return APIResponse.error(
                    "Student ID is required."
                )

            room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            if not room:

                return APIResponse.error(
                    "Room not found."
                )

            current_students = [
                str(student).strip()
                for student in (
                    room.get(
                        "current_students"
                    )
                    or []
                )
                if str(student).strip()
            ]

            if student_id not in current_students:

                return APIResponse.error(
                    "Student is not assigned to this room."
                )

            success = (
                self.repository.remove_student_from_room(
                    firebase_id,
                    student_id,
                )
            )

            if not success:

                return APIResponse.error(
                    "Unable to remove student from room."
                )

            updated_room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            return APIResponse.success(
                "Student removed from room successfully.",
                self._serialize_room(
                    updated_room
                ),
            )

        except Exception as exc:

            logger.exception(
                "Failed to remove student from room."
            )

            return APIResponse.error(
                "Unable to remove student from room.",
                str(exc),
            )

    # =========================================================
    # CHANGE STUDENT ROOM
    # =========================================================

    def change_student_room(
        self,
        from_room_id: str,
        to_room_id: str,
        student_id: str,
    ):

        try:

            from_room_id = str(
                from_room_id or ""
            ).strip()

            to_room_id = str(
                to_room_id or ""
            ).strip()

            student_id = str(
                student_id or ""
            ).strip()

            if not from_room_id:
                return APIResponse.error(
                    "Current room ID is required."
                )

            if not to_room_id:
                return APIResponse.error(
                    "New room ID is required."
                )

            if not student_id:
                return APIResponse.error(
                    "Student ID is required."
                )

            if from_room_id == to_room_id:

                return APIResponse.error(
                    "Source and destination rooms cannot be the same."
                )

            source_room = (
                self.repository.get_room_by_id(
                    from_room_id
                )
            )

            if not source_room:

                return APIResponse.error(
                    "Current room not found."
                )

            destination_room = (
                self.repository.get_room_by_id(
                    to_room_id
                )
            )

            if not destination_room:

                return APIResponse.error(
                    "Destination room not found."
                )

            if not source_room.get(
                "is_active",
                True,
            ):

                return APIResponse.error(
                    "Current room is disabled."
                )

            if not destination_room.get(
                "is_active",
                True,
            ):

                return APIResponse.error(
                    "Destination room is disabled."
                )

            source_students = [
                str(student).strip()
                for student in (
                    source_room.get(
                        "current_students"
                    )
                    or []
                )
                if str(student).strip()
            ]

            if student_id not in source_students:

                return APIResponse.error(
                    "Student is not assigned to the current room."
                )

            destination_students = [
                str(student).strip()
                for student in (
                    destination_room.get(
                        "current_students"
                    )
                    or []
                )
                if str(student).strip()
            ]

            if student_id in destination_students:

                return APIResponse.error(
                    "Student is already assigned to the destination room."
                )

            destination_available_beds = int(
                destination_room.get(
                    "available_beds",
                    0,
                )
                or 0
            )

            if destination_available_beds <= 0:

                return APIResponse.error(
                    "Destination room is already full."
                )

            success = (
                self.repository.change_student_room(
                    from_room_id,
                    to_room_id,
                    student_id,
                )
            )

            if not success:

                return APIResponse.error(
                    "Unable to change student room."
                )

            updated_source = (
                self.repository.get_room_by_id(
                    from_room_id
                )
            )

            updated_destination = (
                self.repository.get_room_by_id(
                    to_room_id
                )
            )

            return APIResponse.success(
                "Student room changed successfully.",
                {
                    "student_id": student_id,
                    "from_room": self._serialize_room(
                        updated_source
                    ),
                    "to_room": self._serialize_room(
                        updated_destination
                    ),
                },
            )

        except ValueError as exc:

            return APIResponse.error(
                str(exc)
            )

        except Exception as exc:

            logger.exception(
                "Failed to change student room."
            )

            return APIResponse.error(
                "Unable to change student room.",
                str(exc),
            )

    # =========================================================
    # ROOM STATISTICS
    # =========================================================

    def get_room_statistics(self):

        try:

            statistics = (
                self.repository.get_room_statistics()
            )

            return APIResponse.success(
                "Room statistics retrieved successfully.",
                statistics,
            )

        except Exception as exc:

            logger.exception(
                "Failed to retrieve room statistics."
            )

            return APIResponse.error(
                "Unable to retrieve room statistics.",
                str(exc),
            )