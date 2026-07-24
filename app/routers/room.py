from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import status

from app.dependencies.auth_dependency import get_current_admin

from app.schemas.room_schema import (
    RoomCreate,
    RoomUpdate,

    RoomCreateResponse,
    RoomUpdateResponse,
    RoomDeleteResponse,

    RoomListResponse,
    RoomSingleResponse,
    RoomSearchResponse,
    RoomCountResponse,
)
from app.services.room_service import RoomService

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)

room_service = RoomService()


# POST
@router.post(
    "/",
    response_model=RoomCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Room",
    description="Create a new hostel room.",
)
def create_room(
    room: RoomCreate,
    current_admin=Depends(get_current_admin),
):
    return room_service.create_room(
        room.model_dump()
    )


# GET ALL
@router.get(
    "/",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get All Rooms",
    description="Retrieve all hostel rooms.",
)
def get_all_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.get_all_rooms()


# SEARCH
@router.get(
    "/search",
    response_model=RoomSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Rooms",
    description="Search rooms by room number, block, room type or status.",
)
def search_rooms(
    keyword: str = Query(
        ...,
        min_length=1,
        description="Enter room number, block, room type or status",
    ),
    current_admin=Depends(get_current_admin),
):
    return room_service.search_rooms(
        keyword
    )


# COUNT
@router.get(
    "/count",
    response_model=RoomCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Count Rooms",
    description="Get the total number of hostel rooms.",
)
def count_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.count_rooms()


# AVAILABLE
@router.get(
    "/available",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Available Rooms",
    description="Retrieve all available hostel rooms.",
)
def get_available_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.get_available_rooms()


# OCCUPIED
@router.get(
    "/occupied",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Occupied Rooms",
    description="Retrieve all occupied hostel rooms.",
)
def get_occupied_rooms(
    current_admin=Depends(get_current_admin),
):
    return room_service.get_occupied_rooms()


# GET BY ID
@router.get(
    "/{firebase_id}",
    response_model=RoomSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Room By ID",
    description="Retrieve a room using Firebase ID.",
)
def get_room_by_id(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.get_room_by_id(
        firebase_id
    )


# UPDATE
@router.put(
    "/{firebase_id}",
    response_model=RoomUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Room",
    description="Update an existing room.",
)
def update_room(
    firebase_id: str,
    room: RoomUpdate,
    current_admin=Depends(get_current_admin),
):
    return room_service.update_room(
        firebase_id,
        room.model_dump(exclude_unset=True),
    )


# DELETE
@router.delete(
    "/{firebase_id}",
    response_model=RoomDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete Room",
    description="Delete a room from the hostel.",
)
def delete_room(
    firebase_id: str,
    current_admin=Depends(get_current_admin),
):
    return room_service.delete_room(
        firebase_id
    )