from fastapi import APIRouter, Depends, Query, status

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


# ============================================================
# CREATE ROOM
# ============================================================

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
    return room_service.create_room(
        room.model_dump()
    )


# ============================================================
# GET ALL ACTIVE ROOMS
# ============================================================

@router.get(
    "/",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get All Rooms",
    description="Retrieve all active hostel rooms.",
    response_description="List of active rooms.",
)
def get_all_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.get_all_rooms()


# ============================================================
# SEARCH ROOMS
# IMPORTANT: Must stay before /{firebase_id}
# ============================================================

@router.get(
    "/search",
    response_model=RoomSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Rooms",
    description="Search active rooms by room number, floor, or status.",
    response_description="Matching rooms.",
)
def search_rooms(
    keyword: str = Query(
        ...,
        min_length=1,
        max_length=50,
        description="Room number, floor, or status keyword.",
        examples=["101"],
    ),
    current_admin=Depends(get_current_admin),
):
    return room_service.search_rooms(keyword)


# ============================================================
# ROOM COUNT
# ============================================================

@router.get(
    "/count",
    response_model=RoomCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Room Count",
    description="Get the total number of active hostel rooms.",
    response_description="Room count.",
)
def count_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.count_rooms()


# ============================================================
# AVAILABLE ROOMS
# ============================================================

@router.get(
    "/available",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Available Rooms",
    description=(
        "Retrieve active rooms that have at least one available bed "
        "for student allocation."
    ),
    response_description="Rooms with available beds.",
)
def get_available_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.get_available_rooms()


# ============================================================
# OCCUPIED ROOMS
# ============================================================

@router.get(
    "/occupied",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Occupied Rooms",
    description=(
        "Retrieve active rooms that currently have one or more "
        "students assigned."
    ),
    response_description="Occupied rooms.",
)
def get_occupied_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.get_occupied_rooms()


# ============================================================
# ROOM ALLOCATION DETAILS
# IMPORTANT: Must stay before /{firebase_id}
# ============================================================

@router.get(
    "/allocation/{firebase_id}",
    response_model=RoomSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Room Allocation Details",
    description=(
        "Retrieve an active room that has available beds before "
        "assigning a student."
    ),
    response_description="Room allocation details.",
)
def get_room_for_allocation(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.get_room_for_allocation(
        firebase_id
    )


# ============================================================
# GET SINGLE ROOM
# ============================================================

@router.get(
    "/{firebase_id}",
    response_model=RoomSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Room",
    description="Retrieve a single room using its Firebase document ID.",
    response_description="Room details.",
)
def get_room_by_id(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.get_room_by_id(
        firebase_id
    )


# ============================================================
# UPDATE ROOM
# ============================================================

@router.put(
    "/{firebase_id}",
    response_model=RoomUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Room",
    description=(
        "Update room information. Occupied and available beds "
        "are calculated by the backend."
    ),
    response_description="Updated room details.",
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


# ============================================================
# DISABLE ROOM
# ============================================================

@router.put(
    "/disable/{firebase_id}",
    response_model=RoomDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable Room",
    description=(
        "Soft-disable a room. A room containing active students "
        "cannot be disabled."
    ),
    response_description="Room disabled successfully.",
)
def disable_room(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.disable_room(
        firebase_id
    )


# ============================================================
# ENABLE ROOM
# ============================================================

@router.put(
    "/enable/{firebase_id}",
    response_model=RoomDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Enable Room",
    description=(
        "Re-enable a previously disabled room."
    ),
    response_description="Room enabled successfully.",
)
def enable_room(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.enable_room(
        firebase_id
    )