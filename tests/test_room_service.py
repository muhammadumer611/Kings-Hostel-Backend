from app.services.room_service import RoomService


class DummyRepository:
    def __init__(self):
        self.rooms = {}
        self.created = []

    def get_room_by_number(self, room_number):
        for room in self.rooms.values():
            if room.get("room_number") == room_number:
                return room
        return None

    def create_room(self, room_data):
        self.created.append(room_data)
        room_id = f"room-{len(self.created)}"
        self.rooms[room_id] = dict(room_data)
        self.rooms[room_id]["firebase_id"] = room_id
        return room_id

    def get_all_rooms(self):
        return list(self.rooms.values())

    def get_room_by_id(self, firebase_id):
        return self.rooms.get(firebase_id)

    def update_room(self, firebase_id, room_data):
        self.rooms[firebase_id].update(room_data)
        return True

    def delete_room(self, firebase_id):
        self.rooms.pop(firebase_id, None)
        return True

    def room_exists(self, firebase_id):
        return firebase_id in self.rooms

    def count_rooms(self):
        return len(self.rooms)

    def search_rooms(self, keyword):
        return [room for room in self.rooms.values() if keyword.lower() in str(room.get("room_number", "")).lower()]

    def get_available_rooms(self):
        return [room for room in self.rooms.values() if room.get("is_active") and room.get("available_beds", 0) > 0]

    def get_occupied_rooms(self):
        return [room for room in self.rooms.values() if room.get("is_active") and room.get("occupied_beds", 0) > 0]

    def disable_room(self, firebase_id):
        self.rooms[firebase_id]["is_active"] = False
        return True

    def enable_room(self, firebase_id):
        self.rooms[firebase_id]["is_active"] = True
        return True

    def assign_student_to_room(self, firebase_id, student_id):
        room = self.rooms[firebase_id]
        students = room.get("current_students") or []
        if student_id in students:
            return False
        students.append(student_id)
        room["current_students"] = students
        room["occupied_beds"] = len(students)
        room["available_beds"] = max(room.get("total_beds", 0) - len(students), 0)
        room["status"] = "Partially Occupied" if len(students) > 0 and len(students) < room.get("total_beds", 0) else "Occupied" if len(students) >= room.get("total_beds", 0) else "Available"
        return True

    def remove_student_from_room(self, firebase_id, student_id):
        room = self.rooms[firebase_id]
        students = room.get("current_students") or []
        if student_id not in students:
            return False
        students.remove(student_id)
        room["current_students"] = students
        room["occupied_beds"] = len(students)
        room["available_beds"] = max(room.get("total_beds", 0) - len(students), 0)
        room["status"] = "Partially Occupied" if len(students) > 0 and len(students) < room.get("total_beds", 0) else "Occupied" if len(students) >= room.get("total_beds", 0) else "Available"
        return True

    def change_student_room(self, from_room_id, to_room_id, student_id):
        from_room = self.rooms[from_room_id]
        to_room = self.rooms[to_room_id]
        if student_id not in from_room.get("current_students", []):
            return False
        if student_id in to_room.get("current_students", []):
            return False
        from_students = [student for student in from_room.get("current_students", []) if student != student_id]
        to_students = list(to_room.get("current_students", [])) + [student_id]
        from_room["current_students"] = from_students
        to_room["current_students"] = to_students
        from_room["occupied_beds"] = len(from_students)
        from_room["available_beds"] = max(from_room.get("total_beds", 0) - len(from_students), 0)
        to_room["occupied_beds"] = len(to_students)
        to_room["available_beds"] = max(to_room.get("total_beds", 0) - len(to_students), 0)
        from_room["status"] = "Partially Occupied" if len(from_students) > 0 and len(from_students) < from_room.get("total_beds", 0) else "Occupied" if len(from_students) >= from_room.get("total_beds", 0) else "Available"
        to_room["status"] = "Partially Occupied" if len(to_students) > 0 and len(to_students) < to_room.get("total_beds", 0) else "Occupied" if len(to_students) >= to_room.get("total_beds", 0) else "Available"
        return True


def test_create_room_normalizes_and_calculates_fields():
    service = RoomService()
    service.repository = DummyRepository()

    result = service.create_room({
        "room_number": " 101 ",
        "floor": 2,
        "total_beds": 4,
        "monthly_fee": 12000,
        "security_deposit": 5000,
    })

    assert result["success"] is True
    assert result["message"] == "Room created successfully."
    assert result["data"]["firebase_id"].startswith("room-")


def test_disable_room_rejects_when_students_are_present():
    service = RoomService()
    service.repository = DummyRepository()
    room_id = service.repository.create_room({
        "room_number": "102",
        "floor": 1,
        "total_beds": 2,
        "monthly_fee": 1000,
        "security_deposit": 200,
        "occupied_beds": 1,
        "current_students": ["STU1"],
        "available_beds": 1,
        "status": "Partially Occupied",
    })

    result = service.disable_room(room_id)

    assert result["success"] is False
    assert result["message"] == "Cannot disable room because students are living in it."


def test_allocate_student_updates_occupancy():
    service = RoomService()
    service.repository = DummyRepository()
    room_id = service.repository.create_room({
        "room_number": "103",
        "floor": 3,
        "total_beds": 2,
        "monthly_fee": 1000,
        "security_deposit": 200,
        "occupied_beds": 0,
        "current_students": [],
        "available_beds": 2,
        "status": "Available",
    })

    result = service.assign_student_to_room(room_id, "STU2")

    assert result["success"] is True
    assert result["message"] == "Student assigned successfully."
    assert service.repository.get_room_by_id(room_id)["occupied_beds"] == 1
    assert service.repository.get_room_by_id(room_id)["available_beds"] == 1
    assert service.repository.get_room_by_id(room_id)["status"] == "Partially Occupied"
