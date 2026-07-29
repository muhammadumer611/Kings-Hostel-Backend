from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status

from app.dependencies.auth_dependency import get_current_admin
from app.schemas.room_schema import (
    RoomCountResponse,
    RoomCreate,
    RoomCreateResponse,
    RoomDeleteResponse,
    RoomListResponse,
    RoomSearchResponse,
    RoomSingleResponse,
    RoomUpdate,
    RoomUpdateResponse,
)
from app.services.room_service import RoomService

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)

ROOM_SERVICE = RoomService()


@router.post(
    "/",
    response_model=RoomCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Room",
)
def create_room(
    room: RoomCreate,
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.create_room(room.model_dump())


@router.get(
    "/",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get All Rooms",
)
def get_all_rooms(
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.get_all_rooms()


@router.get(
    "/search",
    response_model=RoomSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Rooms",
)
def search_rooms(
    keyword: str = Query(..., min_length=1),
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.search_rooms(keyword)


@router.get(
    "/count",
    response_model=RoomCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Room Count",
)
def count_rooms(
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.count_rooms()


@router.get(
    "/available",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Available Rooms",
)
def get_available_rooms(
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.get_available_rooms()


@router.get(
    "/occupied",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Occupied Rooms",
)
def get_occupied_rooms(
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.get_occupied_rooms()


@router.get(
    "/allocation/{firebase_id}",
    response_model=RoomSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Room For Allocation",
)
def get_room_for_allocation(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.get_room_for_allocation(firebase_id)


@router.get(
    "/{firebase_id}",
    response_model=RoomSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Room By ID",
)
def get_room_by_id(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.get_room_by_id(firebase_id)


@router.put(
    "/{firebase_id}",
    response_model=RoomUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Room",
)
def update_room(
    firebase_id: str,
    room: RoomUpdate,
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.update_room(
        firebase_id,
        room.model_dump(exclude_unset=True),
    )


@router.put(
    "/disable/{firebase_id}",
    response_model=RoomDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable Room",
)
def disable_room(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.disable_room(firebase_id)


@router.put(
    "/enable/{firebase_id}",
    response_model=RoomDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable Room",
)
def enable_room(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return ROOM_SERVICE.enable_room(firebase_id)