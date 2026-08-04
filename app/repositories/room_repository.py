from datetime import UTC
from datetime import datetime

from firebase_admin import firestore

from app.firebase.firebase import db
from app.utils.logger import logger


class RoomRepository:

    def __init__(self):
        self.collection = db.collection("rooms")

    def _get_timestamp(self) -> str:
        return datetime.now(UTC).isoformat()

    def _calculate_metrics(self, total_beds: int, occupied_beds: int):
        total_beds = max(int(total_beds or 0), 0)
        occupied_beds = max(int(occupied_beds or 0), 0)
        if occupied_beds > total_beds:
            occupied_beds = total_beds
        available_beds = max(total_beds - occupied_beds, 0)
        if occupied_beds == 0:
            status = "Available"
        elif occupied_beds >= total_beds:
            status = "Occupied"
        else:
            status = "Partially Occupied"
        return occupied_beds, available_beds, status

    def _normalize_room_data(self, room_data: dict) -> dict:
        normalized = dict(room_data or {})
        if "room_number" in normalized:
            normalized["room_number"] = str(normalized.get("room_number", "") or "").strip().upper()
        if "floor" in normalized:
            normalized["floor"] = int(normalized["floor"])
        if "total_beds" in normalized:
            normalized["total_beds"] = int(normalized["total_beds"])
        if "monthly_fee" in normalized:
            normalized["monthly_fee"] = float(normalized["monthly_fee"])
        if "security_deposit" in normalized:
            normalized["security_deposit"] = float(normalized["security_deposit"])
        if "is_active" in normalized:
            normalized["is_active"] = bool(normalized["is_active"])
        if "current_students" in normalized:
            students = normalized.get("current_students") or []
            normalized["current_students"] = [str(student) for student in students if str(student).strip()]
        return normalized

    def create_room(self, room_data: dict):
        try:
            normalized = self._normalize_room_data(room_data)

            if not normalized.get("room_number"):
                raise ValueError("Room number cannot be empty.")

            if self.get_room_by_number(normalized["room_number"]):
                raise ValueError("Room number already exists.")

            if normalized.get("total_beds", 0) <= 0:
                raise ValueError("Total beds must be greater than 0.")

            if normalized.get("monthly_fee", 0) <= 0:
                raise ValueError("Monthly fee must be greater than 0.")

            if normalized.get("security_deposit", 0) < 0:
                raise ValueError("Security deposit cannot be negative.")

            normalized["current_students"] = []
            normalized["occupied_beds"] = 0
            normalized["available_beds"] = normalized["total_beds"]
            normalized["status"] = "Available"
            normalized["is_active"] = bool(normalized.get("is_active", True))
            normalized["created_at"] = self._get_timestamp()
            normalized["updated_at"] = normalized["created_at"]

            room_ref = self.collection.document()
            room_ref.set(normalized)

            logger.info(f"Room created successfully | {room_ref.id}")
            return room_ref.id

        except Exception:
            logger.exception("Failed to create room.")
            raise

    def get_all_rooms(self):
        try:
            rooms = self.collection.where("is_active", "==", True).stream()
            room_list = []

            for room in rooms:
                data = room.to_dict() or {}
                data["firebase_id"] = room.id
                room_list.append(data)

            room_list = sorted(
                room_list,
                key=lambda item: (int(item.get("floor") or 0), str(item.get("room_number") or "").upper()),
            )

            logger.info(f"Rooms retrieved successfully | Total Rooms: {len(room_list)}")
            return room_list

        except Exception:
            logger.exception("Failed to retrieve rooms.")
            raise

    def get_room_by_id(self, firebase_id: str):
        try:
            room = self.collection.document(firebase_id).get()
            if not room.exists:
                return None

            data = room.to_dict() or {}
            data["firebase_id"] = room.id

            logger.info(f"Room retrieved successfully | Firebase ID: {firebase_id}")
            return data

        except Exception:
            logger.exception("Failed to retrieve room by ID.")
            raise

    def get_room_by_number(self, room_number: str):
        try:
            normalized_number = str(room_number or "").strip().upper()
            rooms = (
                self.collection
                .where("room_number", "==", normalized_number)
                .where("is_active", "==", True)
                .limit(1)
                .stream()
            )

            for room in rooms:
                data = room.to_dict() or {}
                data["firebase_id"] = room.id
                logger.info(f"Room found | Room Number: {normalized_number}")
                return data

            return None

        except Exception:
            logger.exception("Failed to retrieve room by number.")
            raise

    def room_exists(self, firebase_id: str):
        try:
            room = self.collection.document(firebase_id).get()
            return room.exists

        except Exception:
            logger.exception("Failed to check room existence.")
            raise

    def count_rooms(self):
        try:
            total_rooms = sum(1 for _ in self.collection.where("is_active", "==", True).stream())
            logger.info(f"Room count retrieved successfully | Total Rooms: {total_rooms}")
            return total_rooms

        except Exception:
            logger.exception("Failed to count rooms.")
            raise

    def update_room(self, firebase_id: str, room_data: dict):
        try:
            room_doc = self.collection.document(firebase_id).get()
            if not room_doc.exists:
                return False

            existing_data = room_doc.to_dict() or {}
            normalized_update = self._normalize_room_data(room_data)

            if not normalized_update:
                return False

            if "room_number" in normalized_update and not normalized_update.get("room_number"):
                raise ValueError("Room number cannot be empty.")
            if "total_beds" in normalized_update:
                if normalized_update["total_beds"] <= 0:
                    raise ValueError("Total beds must be greater than 0.")
                occupied_beds = int(existing_data.get("occupied_beds", 0) or 0)
                if normalized_update["total_beds"] < occupied_beds:
                    raise ValueError("Total beds cannot be less than current occupied beds.")
            if "monthly_fee" in normalized_update and normalized_update["monthly_fee"] <= 0:
                raise ValueError("Monthly fee must be greater than 0.")
            if "security_deposit" in normalized_update and normalized_update["security_deposit"] < 0:
                raise ValueError("Security deposit cannot be negative.")

            total_beds = int(normalized_update.get("total_beds", existing_data.get("total_beds", 0) or 0))
            occupied_beds = int(existing_data.get("occupied_beds", 0) or 0)
            occupied_beds, available_beds, status = self._calculate_metrics(total_beds, occupied_beds)

            normalized_update["occupied_beds"] = occupied_beds
            normalized_update["available_beds"] = available_beds
            normalized_update["status"] = status
            normalized_update["updated_at"] = self._get_timestamp()

            self.collection.document(firebase_id).update(normalized_update)

            logger.info(f"Room updated successfully | Firebase ID: {firebase_id}")
            return True

        except Exception:
            logger.exception("Failed to update room.")
            raise

    def delete_room(self, firebase_id: str):
        try:
            room_doc = self.collection.document(firebase_id).get()

            if not room_doc.exists:
                return False

            room_data = room_doc.to_dict() or {}

            if room_data.get("current_students"):
                raise ValueError("Cannot delete room because students are living in it.")

            self.collection.document(firebase_id).update(
                {
                    "is_active": False,
                    "updated_at": self._get_timestamp(),
                }
            )

            logger.info(f"Room deleted successfully | Firebase ID: {firebase_id}")
            return True

        except Exception:
            logger.exception("Failed to delete room.")
            raise

    def search_rooms(self, keyword: str):
        try:
            keyword = str(keyword or "").strip().lower()
            rooms = self.collection.stream()
            result = []

            for room in rooms:
                data = room.to_dict() or {}
                if not data.get("is_active", True):
                    continue

                room_number = str(data.get("room_number", "")).lower()
                floor = str(data.get("floor", "")).lower()
                status = str(data.get("status", "")).lower()

                if keyword in room_number or keyword in floor or keyword in status:
                    data["firebase_id"] = room.id
                    result.append(data)

            result = sorted(
                result,
                key=lambda item: (int(item.get("floor") or 0), str(item.get("room_number") or "").upper()),
            )

            logger.info(f"Room search completed | Keyword: {keyword} | Results: {len(result)}")
            return result

        except Exception:
            logger.exception("Failed to search rooms.")
            raise

    def get_available_rooms(self):
        try:
            rooms = self.collection.where("is_active", "==", True).stream()
            result = []

            for room in rooms:
                data = room.to_dict() or {}
                if int(data.get("available_beds", 0) or 0) > 0:
                    data["firebase_id"] = room.id
                    result.append(data)

            result = sorted(
                result,
                key=lambda item: (int(item.get("floor") or 0), str(item.get("room_number") or "").upper()),
            )

            logger.info(f"Available rooms retrieved successfully | Total: {len(result)}")
            return result

        except Exception:
            logger.exception("Failed to retrieve available rooms.")
            raise

    def get_occupied_rooms(self):
        try:
            rooms = self.collection.where("is_active", "==", True).stream()
            result = []

            for room in rooms:
                data = room.to_dict() or {}
                if int(data.get("occupied_beds", 0) or 0) > 0:
                    data["firebase_id"] = room.id
                    result.append(data)

            result = sorted(
                result,
                key=lambda item: (int(item.get("floor") or 0), str(item.get("room_number") or "").upper()),
            )

            logger.info(f"Occupied rooms retrieved successfully | Total: {len(result)}")
            return result

        except Exception:
            logger.exception("Failed to retrieve occupied rooms.")
            raise

    def assign_student_to_room(self, firebase_id: str, student_id: str):
        @firestore.transactional
        def _assign(transaction):
            room_ref = self.collection.document(firebase_id)
            room_doc = room_ref.get(transaction=transaction)
            if not room_doc.exists:
                return False

            data = room_doc.to_dict() or {}
            if not data.get("is_active", True):
                raise ValueError("Room is disabled.")

            students = [str(student) for student in (data.get("current_students") or []) if str(student).strip()]
            normalized_student_id = str(student_id).strip()

            if normalized_student_id in students:
                return False

            if int(data.get("available_beds", 0) or 0) <= 0:
                raise ValueError("Room is already full.")

            students.append(normalized_student_id)
            occupied_beds, available_beds, status = self._calculate_metrics(data.get("total_beds", 0), len(students))

            transaction.update(
                room_ref,
                {
                    "current_students": students,
                    "occupied_beds": occupied_beds,
                    "available_beds": available_beds,
                    "status": status,
                    "updated_at": self._get_timestamp(),
                },
            )
            return True

        return _assign()

    def remove_student_from_room(self, firebase_id: str, student_id: str):
        @firestore.transactional
        def _remove(transaction):
            room_ref = self.collection.document(firebase_id)
            room_doc = room_ref.get(transaction=transaction)
            if not room_doc.exists:
                return False

            data = room_doc.to_dict() or {}
            students = [
                str(student)
                for student in (data.get("current_students") or [])
                if str(student).strip()
            ]

            normalized_student_id = str(student_id).strip()

            if normalized_student_id not in students:
                return False

            students.remove(normalized_student_id)
            occupied_beds, available_beds, status = self._calculate_metrics(data.get("total_beds", 0), len(students))

            transaction.update(
                room_ref,
                {
                    "current_students": students,
                    "occupied_beds": occupied_beds,
                    "available_beds": available_beds,
                    "status": status,
                    "updated_at": self._get_timestamp(),
                },
            )
            return True

        return _remove()

    def change_student_room(self, from_room_id: str, to_room_id: str, student_id: str):
        @firestore.transactional
        def _change(transaction):
            from_ref = self.collection.document(from_room_id)
            to_ref = self.collection.document(to_room_id)
            from_doc = from_ref.get(transaction=transaction)
            to_doc = to_ref.get(transaction=transaction)

            if not from_doc.exists or not to_doc.exists or from_room_id == to_room_id:
                return False

            from_data = from_doc.to_dict() or {}
            to_data = to_doc.to_dict() or {}

            if not from_data.get("is_active", True) or not to_data.get("is_active", True):
                raise ValueError("Both rooms must be active.")

            from_students = [str(student) for student in (from_data.get("current_students") or []) if str(student).strip()]
            to_students = [str(student) for student in (to_data.get("current_students") or []) if str(student).strip()]
            normalized_student_id = str(student_id).strip()

            if normalized_student_id not in from_students:
                return False
            if normalized_student_id in to_students:
                return False
            if int(to_data.get("available_beds", 0) or 0) <= 0:
                raise ValueError("Destination room is already full.")

            from_students.remove(normalized_student_id)
            to_students.append(normalized_student_id)

            from_occupied_beds, from_available_beds, from_status = self._calculate_metrics(from_data.get("total_beds", 0), len(from_students))
            to_occupied_beds, to_available_beds, to_status = self._calculate_metrics(to_data.get("total_beds", 0), len(to_students))

            transaction.update(
                from_ref,
                {
                    "current_students": from_students,
                    "occupied_beds": from_occupied_beds,
                    "available_beds": from_available_beds,
                    "status": from_status,
                    "updated_at": self._get_timestamp(),
                },
            )
            transaction.update(
                to_ref,
                {
                    "current_students": to_students,
                    "occupied_beds": to_occupied_beds,
                    "available_beds": to_available_beds,
                    "status": to_status,
                    "updated_at": self._get_timestamp(),
                },
            )
            return True

        return _change()

    def disable_room(self, firebase_id: str):
        try:
            room_doc = self.collection.document(firebase_id).get()

            if not room_doc.exists:
                return False

            room_data = room_doc.to_dict() or {}

            if room_data.get("current_students"):
                raise ValueError("Cannot disable room because students are living in it.")

            self.collection.document(firebase_id).update(
                {
                    "is_active": False,
                    "updated_at": self._get_timestamp(),
                }
            )

            logger.info(f"Room disabled successfully | Firebase ID: {firebase_id}")

            return True

        except Exception:
            logger.exception("Failed to disable room.")
            raise

    def enable_room(self, firebase_id: str):
        try:
            room_doc = self.collection.document(firebase_id).get()

            if not room_doc.exists:
                return False

            self.collection.document(firebase_id).update(
                {
                    "is_active": True,
                    "updated_at": self._get_timestamp(),
                }
            )

            logger.info(f"Room enabled successfully | Firebase ID: {firebase_id}")

            return True

        except Exception:
            logger.exception("Failed to enable room.")
            raise

    def get_rooms_with_available_beds(self):
        try:
            rooms = self.collection.where("is_active", "==", True).stream()

            result = []

            for room in rooms:
                data = room.to_dict() or {}

                if int(data.get("available_beds", 0)) > 0:
                    data["firebase_id"] = room.id
                    result.append(data)

            result = sorted(
                result,
                key=lambda item: (
                    int(item.get("floor") or 0),
                    str(item.get("room_number") or "").upper(),
                ),
            )

            logger.info(
                f"Rooms with available beds retrieved successfully | Total: {len(result)}"
            )

            return result

        except Exception:
            logger.exception("Failed to retrieve rooms with available beds.")
            raise

    def get_room_statistics(self):
        try:
            rooms = self.get_all_rooms()

            total_rooms = len(rooms)

            available_rooms = 0
            occupied_rooms = 0

            total_beds = 0
            occupied_beds = 0
            available_beds = 0

            for room in rooms:
                total_beds += room.get("total_beds", 0)
                occupied_beds += room.get("occupied_beds", 0)
                available_beds += room.get("available_beds", 0)

                if room.get("status") == "Available":
                    available_rooms += 1

                if room.get("occupied_beds", 0) > 0:
                    occupied_rooms += 1

            occupancy_rate = 0

            if total_beds > 0:
                occupancy_rate = round((occupied_beds / total_beds) * 100, 2)

            stats = {
                "total_rooms": total_rooms,
                "available_rooms": available_rooms,
                "occupied_rooms": occupied_rooms,
                "total_beds": total_beds,
                "occupied_beds": occupied_beds,
                "available_beds": available_beds,
                "occupancy_rate": occupancy_rate,
            }

            logger.info(f"Room statistics generated successfully | {stats}")

            return stats

        except Exception:
            logger.exception("Failed to generate room statistics.")
            raise