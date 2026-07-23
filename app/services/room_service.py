from datetime import datetime

from app.repositories.room_repository import RoomRepository
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class RoomService:

    def __init__(self):

        self.repository = RoomRepository()

    def _serialize_room(
        self,
        room: dict,
    ) -> dict:

        """
        Convert Firebase room document
        into frontend response.
        """

        created_at = room.get(
            "created_at"
        )

        updated_at = room.get(
            "updated_at"
        )

        if isinstance(
            created_at,
            datetime,
        ):
            created_at = created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        if isinstance(
            updated_at,
            datetime,
        ):
            updated_at = updated_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        available_beds = (
            room.get(
                "total_beds",
                0,
            )
            -
            room.get(
                "occupied_beds",
                0,
            )
        )

        return {

            "firebase_id": room.get(
                "firebase_id",
                "",
            ),

            "room_number": room.get(
                "room_number",
                "",
            ),

            "block": room.get(
                "block",
                "",
            ),

            "floor": room.get(
                "floor",
                0,
            ),

            "room_type": room.get(
                "room_type",
                "",
            ),

            "total_beds": room.get(
                "total_beds",
                0,
            ),

            "occupied_beds": room.get(
                "occupied_beds",
                0,
            ),

            "available_beds": available_beds,

            "status": room.get(
                "status",
                "Available",
            ),

            "price_per_month": room.get(
                "price_per_month",
                0,
            ),

            "security_deposit": room.get(
                "security_deposit",
                0,
            ),

            "amenities": room.get(
                "amenities",
                [],
            ),

            "created_at": created_at,

            "updated_at": updated_at,
        }

    def create_room(
        self,
        room_data: dict,
    ):

        try:

            existing_room = (
                self.repository.get_room_by_number(
                    room_data.get(
                        "room_number",
                        "",
                    )
                )
            )

            if existing_room:

                logger.warning(
                    "Duplicate room number detected | "
                    f"Room Number: {room_data.get('room_number')}"
                )

                return APIResponse.error(
                    "Room number already exists."
                )

            firebase_id = (
                self.repository.create_room(
                    room_data
                )
            )

            logger.info(
                "Room created successfully | "
                f"Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                "Room created successfully.",
                {
                    "firebase_id": firebase_id,
                },
            )

        except Exception as e:

            logger.exception(
                "Failed to create room."
            )

            return APIResponse.error(
                "Unable to create room.",
                str(e),
            )

    def get_all_rooms(
        self,
    ):

        try:

            rooms = (
                self.repository.get_all_rooms()
            )

            serialized_rooms = [

                self._serialize_room(
                    room
                )

                for room in rooms

            ]

            logger.info(
                "Rooms retrieved successfully | "
                f"Total Rooms: {len(serialized_rooms)}"
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

        except Exception as e:

            logger.exception(
                "Failed to retrieve rooms."
            )

            return APIResponse.error(
                "Unable to retrieve rooms.",
                str(e),
            )

    def get_room_by_id(
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

                logger.warning(
                    "Room not found | "
                    f"Firebase ID: {firebase_id}"
                )

                return APIResponse.error(
                    "Room not found."
                )

            serialized_room = (
                self._serialize_room(
                    room
                )
            )

            logger.info(
                "Room retrieved successfully | "
                f"Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                "Room retrieved successfully.",
                serialized_room,
            )

        except Exception as e:

            logger.exception(
                "Failed to retrieve room."
            )

            return APIResponse.error(
                "Unable to retrieve room.",
                str(e),
            )

    def update_room(
        self,
        firebase_id: str,
        room_data: dict,
    ):

        try:

            room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            if not room:

                logger.warning(
                    "Room not found for update | "
                    f"Firebase ID: {firebase_id}"
                )

                return APIResponse.error(
                    "Room not found."
                )

            update_data = {}

            if (
                "room_number" in room_data
            ):

                room_number = room_data[
                    "room_number"
                ]

                if (
                    room_number
                    != room.get(
                        "room_number"
                    )
                ):

                    existing_room = (
                        self.repository.get_room_by_number(
                            room_number
                        )
                    )

                    if existing_room:

                        logger.warning(
                            "Duplicate room number detected | "
                            f"Room Number: {room_number}"
                        )

                        return APIResponse.error(
                            "Room number already exists."
                        )

                update_data[
                    "room_number"
                ] = room_number

            fields = [

                "block",

                "floor",

                "room_type",

                "total_beds",

                "occupied_beds",

                "status",

                "price_per_month",

                "security_deposit",

                "amenities",

            ]

            for field in fields:

                if field in room_data:

                    update_data[
                        field
                    ] = room_data[
                        field
                    ]

            self.repository.update_room(
                firebase_id,
                update_data,
            )

            updated_room = (
                self.repository.get_room_by_id(
                    firebase_id
                )
            )

            logger.info(
                "Room updated successfully | "
                f"Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                "Room updated successfully.",
                self._serialize_room(
                    updated_room
                ),
            )

        except Exception as e:

            logger.exception(
                "Failed to update room."
            )

            return APIResponse.error(
                "Unable to update room.",
                str(e),
            )

    def delete_room(
        self,
        firebase_id: str,
    ):

        try:

            if not self.repository.room_exists(
                firebase_id
            ):

                logger.warning(
                    "Room not found for deletion | "
                    f"Firebase ID: {firebase_id}"
                )

                return APIResponse.error(
                    "Room not found."
                )

            self.repository.delete_room(
                firebase_id
            )

            logger.info(
                "Room deleted successfully | "
                f"Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                "Room deleted successfully."
            )

        except Exception as e:

            logger.exception(
                "Failed to delete room."
            )

            return APIResponse.error(
                "Unable to delete room.",
                str(e),
            )

    def search_rooms(
        self,
        keyword: str,
    ):

        try:

            keyword = keyword.strip()

            if not keyword:

                return APIResponse.error(
                    "Search keyword is required."
                )

            rooms = (
                self.repository.search_rooms(
                    keyword
                )
            )

            serialized_rooms = [

                self._serialize_room(
                    room
                )

                for room in rooms

            ]

            logger.info(
                "Room search completed | "
                f"Keyword: {keyword} | "
                f"Results: {len(serialized_rooms)}"
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

        except Exception as e:

            logger.exception(
                "Failed to search rooms."
            )

            return APIResponse.error(
                "Unable to search rooms.",
                str(e),
            )

    def count_rooms(
        self,
    ):

        try:

            total_rooms = (
                self.repository.count_rooms()
            )

            logger.info(
                "Room count retrieved successfully | "
                f"Total Rooms: {total_rooms}"
            )

            return APIResponse.success(
                "Room count retrieved successfully.",
                {
                    "total_rooms": total_rooms,
                },
            )

        except Exception as e:

            logger.exception(
                "Failed to count rooms."
            )

            return APIResponse.error(
                "Unable to count rooms.",
                str(e),
            )

    def get_available_rooms(
        self,
    ):

        try:

            rooms = (
                self.repository.get_available_rooms()
            )

            serialized_rooms = [

                self._serialize_room(
                    room
                )

                for room in rooms

            ]

            logger.info(
                "Available rooms retrieved successfully | "
                f"Total Rooms: {len(serialized_rooms)}"
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

        except Exception as e:

            logger.exception(
                "Failed to retrieve available rooms."
            )

            return APIResponse.error(
                "Unable to retrieve available rooms.",
                str(e),
            )

    def get_occupied_rooms(
        self,
    ):

        try:

            rooms = (
                self.repository.get_occupied_rooms()
            )

            serialized_rooms = [

                self._serialize_room(
                    room
                )

                for room in rooms

            ]

            logger.info(
                "Occupied rooms retrieved successfully | "
                f"Total Rooms: {len(serialized_rooms)}"
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

        except Exception as e:

            logger.exception(
                "Failed to retrieve occupied rooms."
            )

            return APIResponse.error(
                "Unable to retrieve occupied rooms.",
                str(e),
            )