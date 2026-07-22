from app.firebase.firebase import db


class RoomRepository:
    def create_room(self, room_data: dict):
        room_ref = db.collection("rooms").document()
        room_ref.set(room_data)
        return room_ref.id

    def get_all_rooms(self):
        rooms = db.collection("rooms").stream()
        result = []
        for room in rooms:
            data = room.to_dict()
            data["firebase_id"] = room.id
            result.append(data)
        return result

    def get_room_by_number(self, room_number: str):
        rooms = (
            db.collection("rooms")
            .where("room_number", "==", room_number)
            .limit(1)
            .stream()
        )
        for room in rooms:
            return room.to_dict()
        return None
