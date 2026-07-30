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

room_service = RoomService()


@router.post(
    "/",
    response_model=RoomCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Room",
    description="Create a new hostel room.",
    response_description="Room created successfully.",
)
def create_room(
    room: RoomCreate,
    current_admin=Depends(get_current_admin),
):
    return room_service.create_room(room.model_dump())


@router.get(
    "/",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get All Rooms",
    description="Retrieve all active rooms.",
    response_description="List of rooms.",
)
def get_all_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.get_all_rooms()


@router.get(
    "/search",
    response_model=RoomSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Rooms",
    description="Search rooms by keyword.",
    response_description="Matching rooms.",
)
def search_rooms(
    keyword: str = Query(..., min_length=1),
    current_admin=Depends(get_current_admin),
):
    return room_service.search_rooms(keyword)


@router.get(
    "/count",
    response_model=RoomCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Room Count",
    description="Get total active rooms.",
    response_description="Room count.",
)
def count_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.count_rooms()


@router.get(
    "/available",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Available Rooms",
    description="Retrieve all available rooms.",
    response_description="Available rooms.",
)
def get_available_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.get_available_rooms()


@router.get(
    "/occupied",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Occupied Rooms",
    description="Retrieve all occupied rooms.",
    response_description="Occupied rooms.",
)
def get_occupied_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.get_occupied_rooms()


@router.get(
    "/allocation/{firebase_id}",
    response_model=RoomSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Room Allocation Details",
    description="Retrieve room details before assigning a student.",
    response_description="Room details.",
)
def get_room_for_allocation(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.get_room_for_allocation(firebase_id)


@router.get(
    "/{firebase_id}",
    response_model=RoomSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Room",
    description="Retrieve room by Firebase ID.",
    response_description="Room details.",
)
def get_room_by_id(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.get_room_by_id(firebase_id)


@router.put(
    "/{firebase_id}",
    response_model=RoomUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Room",
    description="Update room information.",
    response_description="Updated room.",
)
def update_room(
    firebase_id: str,
    room: RoomUpdate,
    current_admin=Depends(get_current_admin),
):
    return room_service.update_room(
        firebase_id,
        room.model_dump(
            exclude_none=True,
            exclude_unset=True,
        ),
    )


@router.put(
    "/disable/{firebase_id}",
    response_model=RoomDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable Room",
    description="Soft delete a room.",
    response_description="Room disabled.",
)
def disable_room(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.disable_room(firebase_id)


@router.put(
    "/enable/{firebase_id}",
    response_model=RoomDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable Room",
    description="Enable a previously disabled room.",
    response_description="Room enabled.",
)
def enable_room(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.enable_room(firebase_id)