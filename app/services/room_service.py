from datetime import datetime

from app.repositories.room_repository import RoomRepository
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class RoomService:

    def __init__(self):
        self.repository = RoomRepository()

    def _format_timestamp(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        if not value:
            return None
        return str(value)

    def _calculate_status(self, occupied_beds: int, total_beds: int) -> str:
        if occupied_beds <= 0:
            return "Available"
        if occupied_beds >= total_beds:
            return "Occupied"
        return "Partially Occupied"

    def _calculate_room_metrics(self, room: dict):
        total_beds = int(room.get("total_beds", 0) or 0)
        occupied_beds = int(room.get("occupied_beds", 0) or 0)
        if occupied_beds < 0:
            occupied_beds = 0
        if occupied_beds > total_beds:
            occupied_beds = total_beds
        available_beds = max(total_beds - occupied_beds, 0)
        status = self._calculate_status(occupied_beds, total_beds)
        return occupied_beds, available_beds, status

    def _serialize_room(self, room: dict):
        occupied_beds, available_beds, status = self._calculate_room_metrics(room)
        return {
            "firebase_id": room.get("firebase_id"),
            "room_number": room.get("room_number"),
            "floor": room.get("floor"),
            "total_beds": int(room.get("total_beds", 0) or 0),
            "occupied_beds": occupied_beds,
            "available_beds": available_beds,
            "status": status,
            "monthly_fee": room.get("monthly_fee"),
            "security_deposit": room.get("security_deposit"),
            "is_active": room.get("is_active", True),
            "current_students": room.get("current_students") or [],
            "created_at": self._format_timestamp(room.get("created_at")),
            "updated_at": self._format_timestamp(room.get("updated_at")),
        }

    def _normalize_room_payload(self, room_data: dict, for_update: bool = False):
        if not isinstance(room_data, dict):
            raise ValueError("Room payload must be a dictionary.")

        normalized = {}

        if "room_number" in room_data:
            room_number = str(room_data.get("room_number", "") or "").strip().upper()
            if not room_number:
                raise ValueError("Room number cannot be empty.")
            normalized["room_number"] = room_number

        if "floor" in room_data:
            normalized["floor"] = int(room_data["floor"])

        if "total_beds" in room_data:
            total_beds = int(room_data["total_beds"])
            if total_beds <= 0:
                raise ValueError("Total beds must be greater than 0.")
            normalized["total_beds"] = total_beds

        if "monthly_fee" in room_data:
            monthly_fee = float(room_data["monthly_fee"])
            if monthly_fee <= 0:
                raise ValueError("Monthly fee must be greater than 0.")
            normalized["monthly_fee"] = monthly_fee

        if "security_deposit" in room_data:
            security_deposit = float(room_data["security_deposit"])
            if security_deposit < 0:
                raise ValueError("Security deposit cannot be negative.")
            normalized["security_deposit"] = security_deposit

        if "is_active" in room_data:
            normalized["is_active"] = bool(room_data["is_active"])

        if for_update and not normalized:
            raise ValueError("No valid fields provided.")

        return normalized

    def create_room(self, room_data: dict):
        try:
            normalized_room = self._normalize_room_payload(room_data)
            existing_room = self.repository.get_room_by_number(normalized_room["room_number"])

            if existing_room:
                return APIResponse.error("Room number already exists.")

            firebase_id = self.repository.create_room(normalized_room)
            return APIResponse.success("Room created successfully.", {"firebase_id": firebase_id})

        except ValueError as exc:
            return APIResponse.error(str(exc))
        except Exception as e:
            logger.exception("Failed to create room.")
            return APIResponse.error("Unable to create room.", str(e))

    def get_all_rooms(self):
        try:
            rooms = self.repository.get_all_rooms()
            serialized_rooms = [self._serialize_room(room) for room in rooms]

            logger.info(f"Rooms retrieved successfully | Total Rooms: {len(serialized_rooms)}")
            return APIResponse.success(
                "Rooms retrieved successfully.",
                {
                    "total_rooms": len(serialized_rooms),
                    "rooms": serialized_rooms,
                },
            )

        except Exception as e:
            logger.exception("Failed to retrieve rooms.")
            return APIResponse.error("Unable to retrieve rooms.", str(e))

    def get_room_by_id(self, firebase_id: str):
        try:
            room = self.repository.get_room_by_id(firebase_id)
            if not room:
                logger.warning(f"Room not found | Firebase ID: {firebase_id}")
                return APIResponse.error("Room not found.")

            serialized_room = self._serialize_room(room)
            logger.info(f"Room retrieved successfully | Firebase ID: {firebase_id}")
            return APIResponse.success("Room retrieved successfully.", serialized_room)

        except Exception as e:
            logger.exception("Failed to retrieve room.")
            return APIResponse.error("Unable to retrieve room.", str(e))

    def update_room(self, firebase_id: str, room_data: dict):
        try:
            room = self.repository.get_room_by_id(firebase_id)
            if not room:
                logger.warning(f"Room not found for update | Firebase ID: {firebase_id}")
                return APIResponse.error("Room not found.")

            update_payload = self._normalize_room_payload(room_data, for_update=True)

            if "room_number" in update_payload:
                existing_room = self.repository.get_room_by_number(update_payload["room_number"])
                if existing_room and existing_room.get("firebase_id") != firebase_id:
                    logger.warning(f"Duplicate room number detected | Room Number: {update_payload['room_number']}")
                    return APIResponse.error("Room number already exists.")

            if "total_beds" in update_payload:
                occupied_beds = int(room.get("occupied_beds", 0) or 0)
                if update_payload["total_beds"] < occupied_beds:
                    return APIResponse.error("Total beds cannot be less than current occupied beds.")

            success = self.repository.update_room(firebase_id, update_payload)
            if not success:
                return APIResponse.error("Room not found.")

            updated_room = self.repository.get_room_by_id(firebase_id)
            logger.info(f"Room updated successfully | Firebase ID: {firebase_id}")
            return APIResponse.success("Room updated successfully.", self._serialize_room(updated_room))

        except ValueError as exc:
            return APIResponse.error(str(exc))
        except Exception as e:
            logger.exception("Failed to update room.")
            return APIResponse.error("Unable to update room.", str(e))

    def delete_room(self, firebase_id: str):
        try:
            if not self.repository.room_exists(firebase_id):
                logger.warning(f"Room not found for deletion | Firebase ID: {firebase_id}")
                return APIResponse.error("Room not found.")

            self.repository.delete_room(firebase_id)
            logger.info(f"Room deleted successfully | Firebase ID: {firebase_id}")
            return APIResponse.success("Room deleted successfully.")

        except Exception as e:
            logger.exception("Failed to delete room.")
            return APIResponse.error("Unable to delete room.", str(e))

    def search_rooms(self, keyword: str):
        try:
            keyword = (keyword or "").strip()
            if not keyword:
                return APIResponse.error("Search keyword is required.")

            rooms = self.repository.search_rooms(keyword)
            serialized_rooms = [self._serialize_room(room) for room in rooms]

            logger.info(f"Room search completed | Keyword: {keyword} | Results: {len(serialized_rooms)}")
            return APIResponse.success(
                "Rooms retrieved successfully.",
                {
                    "total_rooms": len(serialized_rooms),
                    "rooms": serialized_rooms,
                },
            )

        except Exception as e:
            logger.exception("Failed to search rooms.")
            return APIResponse.error("Unable to search rooms.", str(e))

    def count_rooms(self):
        try:
            total_rooms = self.repository.count_rooms()
            logger.info(f"Room count retrieved successfully | Total Rooms: {total_rooms}")
            return APIResponse.success("Room count retrieved successfully.", {"total_rooms": total_rooms})

        except Exception as e:
            logger.exception("Failed to count rooms.")
            return APIResponse.error("Unable to count rooms.", str(e))

    def get_available_rooms(self):
        try:
            rooms = self.repository.get_available_rooms()
            serialized_rooms = [self._serialize_room(room) for room in rooms]

            logger.info(f"Available rooms retrieved successfully | Total Rooms: {len(serialized_rooms)}")
            return APIResponse.success(
                "Available rooms retrieved successfully.",
                {
                    "total_rooms": len(serialized_rooms),
                    "rooms": serialized_rooms,
                },
            )

        except Exception as e:
            logger.exception("Failed to retrieve available rooms.")
            return APIResponse.error("Unable to retrieve available rooms.", str(e))

    def get_occupied_rooms(self):
        try:
            rooms = self.repository.get_occupied_rooms()
            serialized_rooms = [self._serialize_room(room) for room in rooms]

            logger.info(f"Occupied rooms retrieved successfully | Total Rooms: {len(serialized_rooms)}")
            return APIResponse.success(
                "Occupied rooms retrieved successfully.",
                {
                    "total_rooms": len(serialized_rooms),
                    "rooms": serialized_rooms,
                },
            )

        except Exception as e:
            logger.exception("Failed to retrieve occupied rooms.")
            return APIResponse.error("Unable to retrieve occupied rooms.", str(e))

    def get_room_for_allocation(self, firebase_id: str):
        try:
            room = self.repository.get_room_by_id(firebase_id)
            if not room:
                return APIResponse.error("Room not found.")
            if not room.get("is_active", True):
                return APIResponse.error("Room is disabled.")
            if room.get("available_beds", 0) <= 0:
                return APIResponse.error("Room is already full.")

            return APIResponse.success("Room available.", self._serialize_room(room))

        except Exception as e:
            logger.exception("Failed to fetch room.")
            return APIResponse.error("Unable to fetch room.", str(e))

    def disable_room(self, firebase_id: str):
        try:
            room = self.repository.get_room_by_id(firebase_id)
            if not room:
                return APIResponse.error("Room not found.")
            if room.get("current_students") or room.get("occupied_beds", 0) > 0:
                return APIResponse.error("Cannot disable room because students are living in it.")

            self.repository.disable_room(firebase_id)
            return APIResponse.success("Room disabled successfully.")

        except Exception as e:
            logger.exception("Failed to disable room.")
            return APIResponse.error("Unable to disable room.", str(e))

    def enable_room(self, firebase_id: str):
        try:
            room = self.repository.get_room_by_id(firebase_id)
            if not room:
                return APIResponse.error("Room not found.")

            self.repository.enable_room(firebase_id)
            return APIResponse.success("Room enabled successfully.")

        except Exception as e:
            logger.exception("Failed to enable room.")
            return APIResponse.error("Unable to enable room.", str(e))

    def assign_student_to_room(self, firebase_id: str, student_id: str):
        try:
            room = self.repository.get_room_by_id(firebase_id)
            if not room:
                return APIResponse.error("Room not found.")
            if not room.get("is_active", True):
                return APIResponse.error("Room is disabled.")
            if room.get("available_beds", 0) <= 0:
                return APIResponse.error("Room is already full.")
            if str(student_id) in [str(student) for student in (room.get("current_students") or []) if str(student).strip()]:
                return APIResponse.error("Student is already assigned to this room.")

            success = self.repository.assign_student_to_room(firebase_id, str(student_id))
            if not success:
                return APIResponse.error("Unable to assign student to room.")

            updated_room = self.repository.get_room_by_id(firebase_id)
            return APIResponse.success("Student assigned successfully.", self._serialize_room(updated_room))

        except ValueError as exc:
            return APIResponse.error(str(exc))
        except Exception as e:
            logger.exception("Failed to assign student.")
            return APIResponse.error("Unable to assign student to room.", str(e))

    def remove_student_from_room(self, firebase_id: str, student_id: str):
        try:
            room = self.repository.get_room_by_id(firebase_id)
            if not room:
                return APIResponse.error("Room not found.")
            if str(student_id) not in [str(student) for student in (room.get("current_students") or []) if str(student).strip()]:
                return APIResponse.error("Student not found in room.")

            success = self.repository.remove_student_from_room(firebase_id, str(student_id))
            if not success:
                return APIResponse.error("Unable to remove student from room.")

            updated_room = self.repository.get_room_by_id(firebase_id)
            return APIResponse.success("Student removed successfully.", self._serialize_room(updated_room))

        except Exception as e:
            logger.exception("Failed to remove student.")
            return APIResponse.error("Unable to remove student from room.", str(e))

    def change_student_room(self, from_room_id: str, to_room_id: str, student_id: str):
        try:
            if from_room_id == to_room_id:
                return APIResponse.error("Source and destination rooms cannot be the same.")

            success = self.repository.change_student_room(from_room_id, to_room_id, str(student_id))
            if not success:
                return APIResponse.error("Unable to change student room.")

            return APIResponse.success("Student room changed successfully.")

        except ValueError as exc:
            return APIResponse.error(str(exc))
        except Exception as e:
            logger.exception("Failed to change student room.")
            return APIResponse.error("Unable to change student room.", str(e))