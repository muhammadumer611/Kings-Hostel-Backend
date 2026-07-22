from fastapi import APIRouter
from app.schemas.student_schema import StudentCreate
from app.services.student_service import StudentService

router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

student_service = StudentService()


@router.post("/", status_code=201)
def create_student(student: StudentCreate):
    result = student_service.create_student(student.model_dump())
    return result


@router.get("/")
def get_all_students():
    return student_service.get_all_students()


@router.get("/{student_id}")
def get_student_by_id(student_id: str):
    return student_service.get_student_by_id(student_id)