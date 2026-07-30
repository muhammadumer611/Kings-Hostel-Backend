from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth_dependency import get_current_admin

from app.schemas.student_schema import (
    StudentCreate,
    StudentUpdate,
    StudentCreateResponse,
    StudentUpdateResponse,
    StudentDeleteResponse,
    StudentListResponse,
    StudentSingleResponse,
    StudentSearchResponse,
    StudentCountResponse,
)

from app.services.student_service import StudentService


router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

student_service = StudentService()


# ---------------- CREATE STUDENT ----------------
@router.post(
    "/",
    response_model=StudentCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Student",
    description="Create a new hostel student.",
)
def create_student(
    student: StudentCreate,
    current_admin=Depends(get_current_admin),
):
    return student_service.create_student(
        student.model_dump()
    )


# ---------------- GET ALL STUDENTS ----------------
@router.get(
    "/",
    response_model=StudentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get All Students",
    description="Retrieve all active students.",
)
def get_all_students(
    current_admin=Depends(get_current_admin),
):
    return student_service.get_all_students()


# ---------------- SEARCH STUDENTS ----------------
@router.get(
    "/search",
    response_model=StudentSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Students",
    description="Search students by ID, name, CNIC, phone, email, guardian, room etc.",
)
def search_students(
    keyword: str = Query(
        ...,
        min_length=1,
        description="Search keyword",
    ),
    current_admin=Depends(get_current_admin),
):
    return student_service.search_students(keyword)


# ---------------- COUNT STUDENTS ----------------
@router.get(
    "/count",
    response_model=StudentCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Count Students",
    description="Get total number of active students.",
)
def count_students(
    current_admin=Depends(get_current_admin),
):
    return student_service.count_students()


# ---------------- GET STUDENT ----------------
@router.get(
    "/{student_id}",
    response_model=StudentSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student",
    description="Retrieve a student by Student ID.",
)
def get_student_by_id(
    student_id: str,
    current_admin=Depends(get_current_admin),
):
    return student_service.get_student_by_id(student_id)


# ---------------- UPDATE STUDENT ----------------
@router.put(
    "/{student_id}",
    response_model=StudentUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Student",
    description="Update an existing student.",
)
def update_student(
    student_id: str,
    student: StudentUpdate,
    current_admin=Depends(get_current_admin),
):
    return student_service.update_student(
        student_id,
        student.model_dump(exclude_unset=True),
    )


# ---------------- DELETE (DISABLE) STUDENT ----------------
@router.delete(
    "/{student_id}",
    response_model=StudentDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable Student",
    description="Soft delete (disable) a student.",
)
def delete_student(
    student_id: str,
    current_admin=Depends(get_current_admin),
):
    return student_service.delete_student(student_id)