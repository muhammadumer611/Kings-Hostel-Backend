from datetime import UTC
from datetime import datetime

from app.firebase.firebase import db
from app.utils.logger import logger


class RoomRepository:

    def __init__(self):

        self.collection = db.collection("rooms")

    def create_room(
        self,
        room_data: dict,
    ):

        try:

            room_ref = self.collection.document()

            room_data["created_at"] = datetime.now(
                UTC
            )

            room_data["updated_at"] = datetime.now(
                UTC
            )

            room_ref.set(room_data)

            logger.info(
                "Room created successfully | "
                f"Firebase ID: {room_ref.id}"
            )

            return room_ref.id

        except Exception:

            logger.exception(
                "Failed to create room."
            )

            raise

    def get_all_rooms(
        self,
    ):

        try:

            rooms = self.collection.stream()

            room_list = []

            for room in rooms:

                data = room.to_dict()

                data["firebase_id"] = room.id

                room_list.append(data)

            logger.info(
                "Rooms retrieved successfully | "
                f"Total Rooms: {len(room_list)}"
            )

            return room_list

        except Exception:

            logger.exception(
                "Failed to retrieve rooms."
            )

            raise

    def get_room_by_id(
        self,
        firebase_id: str,
    ):

        try:

            room = self.collection.document(
                firebase_id
            ).get()

            if not room.exists:

                return None

            data = room.to_dict()

            data["firebase_id"] = room.id

            logger.info(
                "Room retrieved successfully | "
                f"Firebase ID: {firebase_id}"
            )

            return data

        except Exception:

            logger.exception(
                "Failed to retrieve room by ID."
            )

            raise

    def get_room_by_number(
        self,
        room_number: str,
    ):

        try:

            rooms = (
                self.collection
                .where(
                    "room_number",
                    "==",
                    room_number,
                )
                .limit(1)
                .stream()
            )

            for room in rooms:

                data = room.to_dict()

                data["firebase_id"] = room.id

                logger.info(
                    "Room found | "
                    f"Room Number: {room_number}"
                )

                return data

            return None

        except Exception:

            logger.exception(
                "Failed to retrieve room by number."
            )

            raise

    def room_exists(
        self,
        firebase_id: str,
    ):

        try:

            room = self.collection.document(
                firebase_id
            ).get()

            return room.exists

        except Exception:

            logger.exception(
                "Failed to check room existence."
            )

            raise

    def count_rooms(
        self,
    ):

        try:

            total_rooms = sum(
                1
                for _ in self.collection.stream()
            )

            logger.info(
                "Room count retrieved successfully | "
                f"Total Rooms: {total_rooms}"
            )

            return total_rooms

        except Exception:

            logger.exception(
                "Failed to count rooms."
            )

            raise

    def update_room(
        self,
        firebase_id: str,
        room_data: dict,
    ):

        try:

            room_data["updated_at"] = datetime.now(
                UTC
            )

            self.collection.document(
                firebase_id
            ).update(
                room_data
            )

            logger.info(
                "Room updated successfully | "
                f"Firebase ID: {firebase_id}"
            )

            return True

        except Exception:

            logger.exception(
                "Failed to update room."
            )

            raise

    def delete_room(
        self,
        firebase_id: str,
    ):

        try:

            self.collection.document(
                firebase_id
            ).delete()

            logger.info(
                "Room deleted successfully | "
                f"Firebase ID: {firebase_id}"
            )

            return True

        except Exception:

            logger.exception(
                "Failed to delete room."
            )

            raise

    def search_rooms(
        self,
        keyword: str,
    ):

        try:

            keyword = keyword.lower()

            rooms = self.collection.stream()

            result = []

            for room in rooms:

                data = room.to_dict()

                room_number = str(
                    data.get("room_number", "")
                ).lower()

                block = str(
                    data.get("block", "")
                ).lower()

                room_type = str(
                    data.get("room_type", "")
                ).lower()

                status = str(
                    data.get("status", "")
                ).lower()

                if (
                    keyword in room_number
                    or keyword in block
                    or keyword in room_type
                    or keyword in status
                ):

                    data["firebase_id"] = room.id

                    result.append(data)

            logger.info(
                "Room search completed | "
                f"Keyword: {keyword} | "
                f"Results: {len(result)}"
            )

            return result

        except Exception:

            logger.exception(
                "Failed to search rooms."
            )

            raise

    def get_available_rooms(
        self,
    ):

        try:

            rooms = (
                self.collection
                .where(
                    "status",
                    "==",
                    "Available",
                )
                .stream()
            )

            result = []

            for room in rooms:

                data = room.to_dict()

                data["firebase_id"] = room.id

                result.append(data)

            logger.info(
                "Available rooms retrieved successfully | "
                f"Total: {len(result)}"
            )

            return result

        except Exception:

            logger.exception(
                "Failed to retrieve available rooms."
            )

            raise

    def get_occupied_rooms(
        self,
    ):

        try:

            rooms = (
                self.collection
                .where(
                    "status",
                    "==",
                    "Occupied",
                )
                .stream()
            )

            result = []

            for room in rooms:

                data = room.to_dict()

                data["firebase_id"] = room.id

                result.append(data)

            logger.info(
                "Occupied rooms retrieved successfully | "
                f"Total: {len(result)}"
            )

            return result

        except Exception:

            logger.exception(
                "Failed to retrieve occupied rooms."
            )

            raise