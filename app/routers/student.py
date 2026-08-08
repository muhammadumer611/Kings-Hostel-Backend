from fastapi import APIRouter, Depends, Path, Query, status

from app.dependencies.auth_dependency import get_current_admin
from app.schemas.student_schema import (
    StudentCreate,
    StudentCreateResponse,
    StudentCountResponse,
    StudentDeleteResponse,
    StudentListResponse,
    StudentSearchResponse,
    StudentSingleResponse,
    StudentUpdate,
    StudentUpdateResponse,
)
from app.services.student_service import StudentService


router = APIRouter(
    prefix="/students",
    tags=["Students"],
)


student_service = StudentService()


# ============================================================
# CREATE STUDENT
# ============================================================

@router.post(
    "/",
    response_model=StudentCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Student",
    description=(
        "Create a new hostel student. "
        "CNIC, phone number, guardian information and personal "
        "information are validated before creation."
    ),
    response_description="Student created successfully.",
)
def create_student(
    student: StudentCreate,
    current_admin=Depends(get_current_admin),
):
    return student_service.create_student(
        student.model_dump(
            exclude_none=False,
        )
    )


# ============================================================
# GET ALL ACTIVE STUDENTS
# ============================================================

@router.get(
    "/",
    response_model=StudentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get All Students",
    description="Retrieve all active hostel students.",
    response_description="List of active students.",
)
def get_all_students(
    current_admin=Depends(get_current_admin),
):
    return student_service.get_all_students()


# ============================================================
# SEARCH STUDENTS
# ============================================================

@router.get(
    "/search",
    response_model=StudentSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Students",
    description=(
        "Search active students by Student ID, name, CNIC, phone, "
        "email, guardian information, room, bed, address or fee status."
    ),
    response_description="Matching students.",
)
def search_students(
    keyword: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Search keyword.",
        examples=["Muhammad"],
    ),
    current_admin=Depends(get_current_admin),
):
    return student_service.search_students(keyword)


# ============================================================
# COUNT ACTIVE STUDENTS
# ============================================================

@router.get(
    "/count",
    response_model=StudentCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Count Active Students",
    description="Get the total number of active hostel students.",
    response_description="Active student count.",
)
def count_students(
    current_admin=Depends(get_current_admin),
):
    return student_service.count_students()


# ============================================================
# GET STUDENT BY ID
# ============================================================

@router.get(
    "/{student_id}",
    response_model=StudentSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student",
    description="Retrieve an active student by Student ID.",
    response_description="Student details.",
    responses={
        404: {
            "description": "Student not found.",
        },
    },
)
def get_student_by_id(
    student_id: str = Path(
        ...,
        min_length=1,
        max_length=30,
        description="Unique Student ID.",
        examples=["STD-2026-001"],
    ),
    current_admin=Depends(get_current_admin),
):
    return student_service.get_student_by_id(student_id)


# ============================================================
# UPDATE STUDENT
# ============================================================

@router.patch(
    "/{student_id}",
    response_model=StudentUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Student",
    description=(
        "Partially update an existing student. "
        "Only supplied fields will be modified."
    ),
    response_description="Updated student details.",
    responses={
        404: {
            "description": "Student not found.",
        },
        400: {
            "description": "Invalid update request.",
        },
    },
)
def update_student(
    student: StudentUpdate,
    student_id: str = Path(
        ...,
        min_length=1,
        max_length=30,
        description="Unique Student ID.",
        examples=["STD-2026-001"],
    ),
    current_admin=Depends(get_current_admin),
):
    return student_service.update_student(
        student_id,
        student.model_dump(
            exclude_unset=True,
            exclude_none=False,
        ),
    )


# ============================================================
# DISABLE STUDENT
# ============================================================

@router.delete(
    "/{student_id}",
    response_model=StudentDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable Student",
    description=(
        "Soft delete a student by marking the student as inactive. "
        "The student's Firestore document is preserved."
    ),
    response_description="Student disabled successfully.",
    responses={
        404: {
            "description": "Student not found.",
        },
    },
)
def delete_student(
    student_id: str = Path(
        ...,
        min_length=1,
        max_length=30,
        description="Unique Student ID.",
        examples=["STD-2026-001"],
    ),
    current_admin=Depends(get_current_admin),
):
    return student_service.delete_student(student_id)