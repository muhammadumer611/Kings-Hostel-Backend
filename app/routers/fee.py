from fastapi import APIRouter
from fastapi import Path
from fastapi import Query

from app.schemas.fee_schema import (
    FeeApproveRequest,
    FeeCreate,
    FeeUpdate,
)
from app.services.fee_service import FeeService

router = APIRouter(
    prefix="/fees",
    tags=["Fees"],
)

fee_service = FeeService()


# ==========================================================
# CREATE
# ==========================================================

@router.post("/", status_code=201)
def create_fee_record(
    fee: FeeCreate,
):
    return fee_service.create_fee_record(
        fee.model_dump()
    )


# ==========================================================
# GET ALL
# ==========================================================

@router.get("/")
def get_all_fee_records():
    return fee_service.get_all_fee_records()


# ==========================================================
# SEARCH
# ==========================================================

@router.get("/search/")
def search_fee_records(
    keyword: str = Query(...)
):
    return fee_service.search_fee_records(
        keyword
    )


# ==========================================================
# COUNT
# ==========================================================

@router.get("/count/")
def count_fee_records():
    return fee_service.count_fee_records()


# ==========================================================
# STATISTICS
# ==========================================================

@router.get("/statistics/")
def get_fee_statistics():
    return fee_service.get_fee_statistics()


# ==========================================================
# PENDING
# ==========================================================

@router.get("/status/pending")
def get_pending_fee_records():
    return fee_service.get_pending_fee_records()


# ==========================================================
# PAID
# ==========================================================

@router.get("/status/paid")
def get_paid_fee_records():
    return fee_service.get_paid_fee_records()


# ==========================================================
# OVERDUE
# ==========================================================

@router.get("/status/overdue")
def get_overdue_fee_records():
    return fee_service.get_overdue_fee_records()


# ==========================================================
# GET BY STUDENT ID
# ==========================================================

@router.get("/student/{student_id}")
def get_fee_by_student_id(
    student_id: str = Path(...)
):
    return fee_service.get_fee_by_student_id(
        student_id
    )


# ==========================================================
# GET BY RECEIPT NUMBER
# ==========================================================

@router.get("/receipt/{receipt_no}")
def get_fee_by_receipt_no(
    receipt_no: str = Path(...)
):
    return fee_service.get_fee_by_receipt_no(
        receipt_no
    )


# ==========================================================
# GET BY FIREBASE ID
# (must stay last among GET routes — it's a catch-all dynamic
# path and would otherwise swallow /search, /count, /statistics,
# /status/*, /student/*, and /receipt/* requests above it)
# ==========================================================

@router.get("/{firebase_id}")
def get_fee_by_firebase_id(
    firebase_id: str = Path(...)
):
    return fee_service.get_fee_by_firebase_id(
        firebase_id
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.put("/{firebase_id}")
def update_fee_record(
    firebase_id: str,
    fee: FeeUpdate,
):
    return fee_service.update_fee_record(
        firebase_id,
        fee.model_dump(exclude_unset=True),
    )


# ==========================================================
# APPROVE PAYMENT
# ==========================================================

@router.put("/{firebase_id}/approve")
def approve_fee_payment(
    firebase_id: str,
    payment: FeeApproveRequest,
):
    return fee_service.approve_fee_payment(
        firebase_id=firebase_id,
        payment_date=payment.payment_date,
        approved_by=payment.approved_by,
        transaction_id=payment.transaction_id,
        payment_method=payment.payment_method,
    )


# ==========================================================
# DISABLE
# ==========================================================

@router.delete("/{firebase_id}")
def disable_fee_record(
    firebase_id: str,
):
    return fee_service.disable_fee_record(
        firebase_id
    )


# ==========================================================
# ENABLE
# ==========================================================

@router.patch("/{firebase_id}/enable")
def enable_fee_record(
    firebase_id: str,
):
    return fee_service.enable_fee_record(
        firebase_id
    )