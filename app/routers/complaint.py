from fastapi import APIRouter
from app.schemas.complaint_schema import ComplaintCreate
from app.services.complaint_service import ComplaintService

router = APIRouter(prefix="/complaints", tags=["Complaints"])
complaint_service = ComplaintService()


@router.post("/", status_code=201)
def create_complaint(complaint: ComplaintCreate):
    return complaint_service.create_complaint(complaint.model_dump())


@router.get("/")
def get_all_complaints():
    return complaint_service.get_all_complaints()
