from fastapi import APIRouter
from app.schemas.fee_schema import FeeRecordCreate
from app.services.fee_service import FeeService

router = APIRouter(prefix="/fees", tags=["Fees"])
fee_service = FeeService()


@router.post("/", status_code=201)
def create_fee_record(fee: FeeRecordCreate):
    return fee_service.create_fee_record(fee.model_dump())


@router.get("/")
def get_all_fee_records():
    return fee_service.get_all_fee_records()
