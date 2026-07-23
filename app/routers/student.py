from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from app.dependencies.auth_dependency import get_current_admin

from app.schemas.student_schema import (
    StudentCreate,
    StudentUpdate,
    StudentCreateResponse,
    StudentUpdateResponse,
    StudentListResponse,
    StudentSingleResponse,
)

from app.services.student_service import StudentService 
router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

student_service = StudentService()
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
@router.get(
    "/",
    response_model=StudentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get All Students",
    description="Retrieve all students from the hostel.",
)
def get_all_students(
    current_admin=Depends(get_current_admin),
):
    return student_service.get_all_students()
@router.get(
    "/{student_id}",
    response_model=StudentSingleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student By ID",
    description="Retrieve a single student using the Student ID.",
)
def get_student_by_id(
    student_id: str,
    current_admin=Depends(get_current_admin),
):
    return student_service.get_student_by_id(
        student_id
    )
@router.put(
    "/{student_id}",
    response_model=StudentUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Student",
    description="Update an existing student's information.",
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