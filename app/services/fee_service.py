from app.repositories.fee_repository import FeeRepository
from app.utils.api_response import APIResponse
from app.utils.logger import logger
from app.utils.receipt_generator import ReceiptGenerator


class FeeService:

    def __init__(self):
        self.repository = FeeRepository()
        self.receipt_generator = ReceiptGenerator()

    def _serialize_fee(self, fee: dict):

        return {
            "firebase_id": fee.get("firebase_id"),

            "receipt_no": fee.get("receipt_no"),

            "student_id": fee.get("student_id"),
            "student_firebase_id": fee.get("student_firebase_id"),
            "student_name": fee.get("student_name"),

            "room_number": fee.get("room_number"),
            "block": fee.get("block"),

            "month": fee.get("month"),
            "year": fee.get("year"),

            "amount": fee.get("amount"),
            "discount": fee.get("discount"),
            "late_fee": fee.get("late_fee"),
            "remaining_amount": fee.get("remaining_amount"),

            "status": fee.get("status"),

            "due_date": fee.get("due_date"),
            "payment_date": fee.get("payment_date"),

            "payment_method": fee.get("payment_method"),
            "transaction_id": fee.get("transaction_id"),

            "notes": fee.get("notes"),

            "approved_by": fee.get("approved_by"),
            "approved_at": (
                fee.get("approved_at").isoformat()
                if hasattr(fee.get("approved_at"), "isoformat")
                else fee.get("approved_at")
            ),

            "created_at": (
                fee.get("created_at").isoformat()
                if hasattr(fee.get("created_at"), "isoformat")
                else fee.get("created_at")
            ),
            "updated_at": (
                fee.get("updated_at").isoformat()
                if hasattr(fee.get("updated_at"), "isoformat")
                else fee.get("updated_at")
            ),
            "is_late": fee.get("is_late", False),
        }

    def _serialize_fee_list(self, fees: list[dict]) -> list[dict]:
        return [
            self._serialize_fee(fee)
            for fee in fees
        ]

    def _validate_duplicate_fee(
        self,
        student_id: str,
        month: str,
        year: int,
    ):
        if self.repository.fee_exists(
            student_id,
            month,
            year,
        ):
            return APIResponse.error(
                message="Fee record already exists for this month.",
                errors=[
                    "Duplicate fee record."
                ],
            )

        return None

    def create_fee_record(self, fee_data: dict):
        try:
            duplicate = self._validate_duplicate_fee(
                student_id=fee_data["student_id"],
                month=fee_data["month"],
                year=fee_data["year"],
            )

            if duplicate:
                return duplicate

            fee_data["receipt_no"] = self.receipt_generator.generate()

            firebase_id = self.repository.create_fee_record(fee_data)

            fee = self.repository.get_fee_by_firebase_id(firebase_id)

            logger.info(
                f"Fee record created successfully | Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                message="Fee record created successfully.",
                data=self._serialize_fee(fee),
            )

        except KeyError as e:
            logger.exception("Required fee field is missing.")

            return APIResponse.error(
                message="Required fee data is missing.",
                errors=[str(e)],
            )

        except Exception:
            logger.exception("Failed to create fee record.")

            return APIResponse.error(
                message="Failed to create fee record.",
                errors=["Internal server error."],
            )

    def get_fee_by_firebase_id(
        self,
        firebase_id: str,
    ):
        try:
            firebase_id = str(firebase_id).strip()

            fee = self.repository.get_fee_by_firebase_id(
                firebase_id
            )

            if not fee:
                return APIResponse.error(
                    message="Fee record not found.",
                    errors=[
                        "Invalid Firebase ID.",
                    ],
                )

            logger.info(
                f"Fee record retrieved successfully | Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                message="Fee record retrieved successfully.",
                data=self._serialize_fee(fee),
            )

        except Exception:
            logger.exception(
                "Failed to retrieve fee record."
            )

            return APIResponse.error(
                message="Failed to retrieve fee record.",
                errors=[
                    "Internal server error.",
                ],
            )

    def get_all_fee_records(self):
        try:
            fees = self.repository.get_all_fee_records()

            logger.info(
                f"Retrieved {len(fees)} fee records successfully."
            )

            return APIResponse.success(
                message="Fee records retrieved successfully.",
                data={
                    "fee_records": self._serialize_fee_list(fees),
                    "total_records": len(fees),
                },
            )

        except Exception:
            logger.exception(
                "Failed to retrieve fee records."
            )

            return APIResponse.error(
                message="Failed to retrieve fee records.",
                errors=[
                    "Internal server error.",
                ],
            )

    def get_fee_by_student_id(
        self,
        student_id: str,
    ):
        try:
            student_id = str(student_id).strip().upper()

            fees = self.repository.get_fee_by_student_id(
                student_id
            )

            logger.info(
                f"Retrieved {len(fees)} fee records | Student ID: {student_id}"
            )

            return APIResponse.success(
                message="Student fee records retrieved successfully.",
                data={
                    "student_id": student_id,
                    "fee_records": self._serialize_fee_list(fees),
                    "total_records": len(fees),
                },
            )

        except Exception:
            logger.exception(
                "Failed to retrieve student fee records."
            )

            return APIResponse.error(
                message="Failed to retrieve student fee records.",
                errors=[
                    "Internal server error.",
                ],
            )

    def search_fee_records(
        self,
        keyword: str,
    ):
        try:
            keyword = str(keyword).strip()

            if not keyword:
                return APIResponse.error(
                    message="Search keyword is required.",
                    errors=[
                        "Keyword cannot be empty.",
                    ],
                )

            fees = self.repository.search_fee_records(
                keyword
            )

            logger.info(
                f"Fee search completed | Keyword: {keyword} | Results: {len(fees)}"
            )

            return APIResponse.success(
                message="Fee records retrieved successfully.",
                data={
                    "keyword": keyword,
                    "fee_records": self._serialize_fee_list(fees),
                    "total_records": len(fees),
                },
            )

        except Exception:
            logger.exception(
                "Failed to search fee records."
            )

            return APIResponse.error(
                message="Failed to search fee records.",
                errors=[
                    "Internal server error.",
                ],
            )

    def update_fee_record(
        self,
        firebase_id: str,
        fee_data: dict,
    ):
        try:
            firebase_id = str(firebase_id).strip()

            if not fee_data:
                return APIResponse.error(
                    message="No update data provided.",
                    errors=[
                        "Fee data cannot be empty.",
                    ],
                )

            fee = self.repository.get_fee_by_firebase_id(
                firebase_id
            )

            if not fee:
                return APIResponse.error(
                    message="Fee record not found.",
                    errors=[
                        "Invalid Firebase ID.",
                    ],
                )

            updated = self.repository.update_fee_record(
                firebase_id,
                fee_data,
            )

            if not updated:
                return APIResponse.error(
                    message="Failed to update fee record.",
                    errors=[
                        "Fee record could not be updated.",
                    ],
                )

            updated_fee = self.repository.get_fee_by_firebase_id(
                firebase_id
            )

            logger.info(
                f"Fee record updated successfully | Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                message="Fee record updated successfully.",
                data=self._serialize_fee(updated_fee),
            )

        except Exception:
            logger.exception(
                "Failed to update fee record."
            )

            return APIResponse.error(
                message="Failed to update fee record.",
                errors=[
                    "Internal server error.",
                ],
            )

    def approve_fee_payment(
        self,
        firebase_id: str,
        payment_date: str,
        approved_by: str,
        transaction_id: str | None = None,
        payment_method: str | None = None,
    ):
        try:
            firebase_id = str(firebase_id).strip()

            fee = self.repository.get_fee_by_firebase_id(
                firebase_id
            )

            if not fee:
                return APIResponse.error(
                    message="Fee record not found.",
                    errors=[
                        "Invalid Firebase ID.",
                    ],
                )

            if fee.get("status") == "Paid":
                return APIResponse.error(
                    message="Fee has already been paid.",
                    errors=[
                        "Duplicate payment is not allowed.",
                    ],
                )

            approved = self.repository.approve_fee_payment(
                firebase_id=firebase_id,
                payment_date=payment_date,
                approved_by=approved_by,
                transaction_id=transaction_id,
                payment_method=payment_method,
            )

            if not approved:
                return APIResponse.error(
                    message="Failed to approve fee payment.",
                    errors=[
                        "Payment approval failed.",
                    ],
                )

            updated_fee = self.repository.get_fee_by_firebase_id(
                firebase_id
            )

            logger.info(
                f"Fee payment approved successfully | Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                message="Fee payment approved successfully.",
                data=self._serialize_fee(updated_fee),
            )

        except Exception:
            logger.exception(
                "Failed to approve fee payment."
            )

            return APIResponse.error(
                message="Failed to approve fee payment.",
                errors=[
                    "Internal server error.",
                ],
            )

    def disable_fee_record(
        self,
        firebase_id: str,
    ):
        try:
            firebase_id = str(firebase_id).strip()

            fee = self.repository.get_fee_by_firebase_id(
                firebase_id
            )

            if not fee:
                return APIResponse.error(
                    message="Fee record not found.",
                    errors=[
                        "Invalid Firebase ID.",
                    ],
                )

            if not fee.get("is_active", True):
                return APIResponse.error(
                    message="Fee record is already disabled.",
                    errors=[
                        "Record is already inactive.",
                    ],
                )

            self.repository.disable_fee_record(
                firebase_id
            )

            logger.info(
                f"Fee record disabled successfully | Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                message="Fee record disabled successfully.",
                data=None,
            )

        except Exception:
            logger.exception(
                "Failed to disable fee record."
            )

            return APIResponse.error(
                message="Failed to disable fee record.",
                errors=[
                    "Internal server error.",
                ],
            )

    def enable_fee_record(
        self,
        firebase_id: str,
    ):
        try:
            firebase_id = str(firebase_id).strip()

            fee = self.repository.get_fee_by_firebase_id(
                firebase_id
            )

            if not fee:
                return APIResponse.error(
                    message="Fee record not found.",
                    errors=[
                        "Invalid Firebase ID.",
                    ],
                )

            if fee.get("is_active", True):
                return APIResponse.error(
                    message="Fee record is already active.",
                    errors=[
                        "Record is already active.",
                    ],
                )

            self.repository.enable_fee_record(
                firebase_id
            )

            logger.info(
                f"Fee record enabled successfully | Firebase ID: {firebase_id}"
            )

            return APIResponse.success(
                message="Fee record enabled successfully.",
                data=None,
            )

        except Exception:
            logger.exception(
                "Failed to enable fee record."
            )

            return APIResponse.error(
                message="Failed to enable fee record.",
                errors=[
                    "Internal server error.",
                ],
            )

    def get_pending_fee_records(self):
        try:
            fees = self.repository.get_pending_fee_records()

            logger.info(
                f"Retrieved {len(fees)} pending fee records."
            )

            return APIResponse.success(
                message="Pending fee records retrieved successfully.",
                data={
                    "fee_records": self._serialize_fee_list(fees),
                    "total_records": len(fees),
                },
            )

        except Exception:
            logger.exception(
                "Failed to retrieve pending fee records."
            )

            return APIResponse.error(
                message="Failed to retrieve pending fee records.",
                errors=[
                    "Internal server error.",
                ],
            )

    def get_paid_fee_records(self):
        try:
            fees = self.repository.get_paid_fee_records()

            logger.info(
                f"Retrieved {len(fees)} paid fee records."
            )

            return APIResponse.success(
                message="Paid fee records retrieved successfully.",
                data={
                    "fee_records": self._serialize_fee_list(fees),
                    "total_records": len(fees),
                },
            )

        except Exception:
            logger.exception(
                "Failed to retrieve paid fee records."
            )

            return APIResponse.error(
                message="Failed to retrieve paid fee records.",
                errors=[
                    "Internal server error.",
                ],
            )

    def get_overdue_fee_records(self):
        try:
            fees = self.repository.get_overdue_fee_records()

            logger.info(
                f"Retrieved {len(fees)} overdue fee records."
            )

            return APIResponse.success(
                message="Overdue fee records retrieved successfully.",
                data={
                    "fee_records": self._serialize_fee_list(fees),
                    "total_records": len(fees),
                },
            )

        except Exception:
            logger.exception(
                "Failed to retrieve overdue fee records."
            )

            return APIResponse.error(
                message="Failed to retrieve overdue fee records.",
                errors=[
                    "Internal server error.",
                ],
            )

    def get_fee_statistics(self):
        try:
            statistics = self.repository.get_fee_statistics()

            logger.info(
                "Fee statistics retrieved successfully."
            )

            return APIResponse.success(
                message="Fee statistics retrieved successfully.",
                data=statistics,
            )

        except Exception:
            logger.exception(
                "Failed to retrieve fee statistics."
            )

            return APIResponse.error(
                message="Failed to retrieve fee statistics.",
                errors=[
                    "Internal server error.",
                ],
            )

    def get_latest_fee(
        self,
        student_id: str,
    ):
        try:
            fee = self.repository.get_latest_fee(
                student_id
            )

            if not fee:
                return APIResponse.error(
                    message="No fee record found.",
                    errors=[
                        "Student has no fee records.",
                    ],
                )

            logger.info(
                f"Latest fee retrieved | Student ID: {student_id}"
            )

            return APIResponse.success(
                message="Latest fee record retrieved successfully.",
                data=self._serialize_fee(fee),
            )

        except Exception:
            logger.exception(
                "Failed to retrieve latest fee."
            )

            return APIResponse.error(
                message="Failed to retrieve latest fee.",
                errors=[
                    "Internal server error.",
                ],
            )

    def get_fee_by_student_month_year(
        self,
        student_id: str,
        month: str,
        year: int,
    ):
        try:
            fee = self.repository.get_fee_by_student_month_year(
                student_id,
                month,
                year,
            )

            if not fee:
                return APIResponse.error(
                    message="Fee record not found.",
                    errors=[
                        "No fee exists for the selected month.",
                    ],
                )

            logger.info(
                f"Fee retrieved | Student ID: {student_id} | Month: {month} | Year: {year}"
            )

            return APIResponse.success(
                message="Fee record retrieved successfully.",
                data=self._serialize_fee(fee),
            )

        except Exception:
            logger.exception(
                "Failed to retrieve fee record."
            )

            return APIResponse.error(
                message="Failed to retrieve fee record.",
                errors=[
                    "Internal server error.",
                ],
            )