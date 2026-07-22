from fastapi import APIRouter
from app.schemas.room_schema import RoomCreate, RoomUpdate
from app.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])
room_service = RoomService()


@router.post("/", status_code=201)
def create_room(room: RoomCreate):
    return room_service.create_room(room.model_dump())


@router.get("/")
def get_all_rooms():
    return room_service.get_all_rooms()
