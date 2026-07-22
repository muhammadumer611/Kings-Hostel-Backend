from app.repositories.room_repository import RoomRepository


class RoomService:
    def __init__(self):
        self.repository = RoomRepository()

    def create_room(self, room_data: dict):
        if self.repository.get_room_by_number(room_data.get("room_number", "")):
            return {
                "success": False,
                "message": "Room number already exists.",
                "data": None,
                "errors": None,
            }

        firebase_id = self.repository.create_room(room_data)
        return {
            "success": True,
            "message": "Room created successfully.",
            "data": {"firebase_id": firebase_id},
            "errors": None,
        }

    def get_all_rooms(self):
        rooms = self.repository.get_all_rooms()
        return {
            "success": True,
            "message": "Rooms retrieved successfully.",
            "data": {"rooms": rooms},
            "errors": None,
        }
