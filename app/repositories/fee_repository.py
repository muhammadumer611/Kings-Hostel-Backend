from datetime import UTC, datetime

from app.firebase.firebase import db
from app.utils.logger import logger


class FeeRepository:

    def __init__(self):
        self.collection = db.collection("fees")

    def _fee_to_dict(self, fee):
        data = fee.to_dict() or {}
        data["firebase_id"] = fee.id
        return data

    def _timestamp(self):
        return datetime.now(UTC).isoformat()

    def _active_query(self):
        return self.collection.where("is_active", "==", True)

    def _fee_query(self):
        return self._active_query()

    def _sort_fees(self, fee_list):
        return sorted(
            fee_list,
            key=lambda x: str(x.get("created_at", "")),
            reverse=True,
        )

    def _prepare_fee_data(self, fee_data: dict):
        fee = dict(fee_data)

        fee.setdefault("status", "Pending")
        fee.setdefault("payment_method", None)
        fee.setdefault("transaction_id", None)
        fee.setdefault("notes", None)
        fee.setdefault("payment_date", None)
        fee.setdefault("approved_by", None)
        fee.setdefault("approved_at", None)
        fee.setdefault("late_fee", 0.0)
        fee.setdefault("remaining_amount", 0.0)
        fee.setdefault("discount", 0.0)
        fee.setdefault("student_firebase_id", None)
        fee.setdefault("receipt_no", None)
        fee.setdefault("is_late", False)
        fee.setdefault("due_date", None)

        fee["is_active"] = True

        timestamp = self._timestamp()

        fee["created_at"] = timestamp
        fee["updated_at"] = timestamp

        return fee

    def _prepare_update_data(self, fee_data: dict):
        fee = dict(fee_data)

        # Immutable fields — never allowed through a generic update.
        fee.pop("firebase_id", None)
        fee.pop("created_at", None)
        fee.pop("receipt_no", None)
        fee.pop("student_id", None)
        fee.pop("student_firebase_id", None)

        fee["updated_at"] = self._timestamp()

        return fee

    def create_fee_record(self, fee_data: dict):
        try:
            fee_data = self._prepare_fee_data(fee_data)

            fee_ref = self.collection.document()

            fee_ref.set(fee_data)

            logger.info(
                f"Fee record created successfully | Firebase ID: {fee_ref.id}"
            )

            return fee_ref.id

        except Exception:
            logger.exception("Failed to create fee record.")
            raise

    def get_fee_by_firebase_id(self, firebase_id: str):
        try:
            firebase_id = str(firebase_id).strip()

            fee = self.collection.document(firebase_id).get()

            if not fee.exists:
                return None

            data = self._fee_to_dict(fee)

            logger.info(
                f"Fee record retrieved successfully | Firebase ID: {firebase_id}"
            )

            return data

        except Exception:
            logger.exception("Failed to retrieve fee record by Firebase ID.")
            raise

    def get_fee_by_student_id(self, student_id: str):
        try:
            student_id = str(student_id).strip().upper()

            fees = (
                self._fee_query()
                .where("student_id", "==", student_id)
                .stream()
            )

            fee_list = []

            for fee in fees:
                fee_list.append(
                    self._fee_to_dict(fee)
                )

            fee_list = self._sort_fees(fee_list)

            logger.info(
                f"Fetched {len(fee_list)} fee records | Student ID: {student_id}"
            )

            return fee_list

        except Exception:
            logger.exception(
                "Failed to retrieve fee records by Student ID."
            )
            raise

    def get_fee_by_receipt_no(self, receipt_no: str):
        try:
            receipt_no = str(receipt_no).strip().upper()

            fees = (
                self._fee_query()
                .where("receipt_no", "==", receipt_no)
                .limit(1)
                .stream()
            )

            for fee in fees:
                data = self._fee_to_dict(fee)

                logger.info(
                    f"Fee record retrieved successfully | Receipt No: {receipt_no}"
                )

                return data

            return None

        except Exception:
            logger.exception(
                "Failed to retrieve fee record by Receipt Number."
            )
            raise

    def get_fee_by_status(self, status: str):
        try:
            status = str(status).strip().title()

            fees = (
                self._fee_query()
                .where("status", "==", status)
                .stream()
            )

            fee_list = [
                self._fee_to_dict(fee)
                for fee in fees
            ]

            fee_list = self._sort_fees(fee_list)

            logger.info(
                f"Fetched {len(fee_list)} fee records | Status: {status}"
            )

            return fee_list

        except Exception:
            logger.exception(
                "Failed to retrieve fee records by status."
            )
            raise

    def get_all_fee_records(self):
        try:
            fees = self._fee_query().stream()

            fee_list = []

            for fee in fees:
                fee_list.append(
                    self._fee_to_dict(fee)
                )

            fee_list = self._sort_fees(fee_list)

            logger.info(
                f"Fetched {len(fee_list)} fee records."
            )

            return fee_list

        except Exception:
            logger.exception(
                "Failed to fetch fee records."
            )
            raise

    def count_fee_records(self):
        try:
            total = sum(
                1 for _ in self._fee_query().stream()
            )

            logger.info(
                f"Fee records counted successfully | Total: {total}"
            )

            return total

        except Exception:
            logger.exception(
                "Failed to count fee records."
            )
            raise

    def get_pending_fee_records(self):
        try:
            fees = (
                self._fee_query()
                .where("status", "==", "Pending")
                .stream()
            )

            fee_list = []

            for fee in fees:
                fee_list.append(
                    self._fee_to_dict(fee)
                )

            fee_list = self._sort_fees(fee_list)

            logger.info(
                f"Fetched {len(fee_list)} pending fee records."
            )

            return fee_list

        except Exception:
            logger.exception(
                "Failed to retrieve pending fee records."
            )
            raise

    def get_paid_fee_records(self):
        try:
            fees = (
                self._fee_query()
                .where("status", "==", "Paid")
                .stream()
            )

            fee_list = []

            for fee in fees:
                fee_list.append(
                    self._fee_to_dict(fee)
                )

            fee_list = self._sort_fees(fee_list)

            logger.info(
                f"Fetched {len(fee_list)} paid fee records."
            )

            return fee_list

        except Exception:
            logger.exception(
                "Failed to retrieve paid fee records."
            )
            raise

    def get_overdue_fee_records(self):
        """
        Fee records that are still Pending and whose due_date has
        already passed. due_date is stored as an ISO string
        (YYYY-MM-DD or full ISO timestamp), so a plain string
        comparison against today's ISO date works directly.
        """
        try:
            today = datetime.now(UTC).date().isoformat()

            fees = (
                self._fee_query()
                .where("status", "==", "Pending")
                .stream()
            )

            fee_list = []

            for fee in fees:
                data = self._fee_to_dict(fee)

                due_date = data.get("due_date")

                if not due_date:
                    continue

                # Compare only the date portion in case due_date
                # is stored as a full ISO timestamp.
                due_date_only = str(due_date)[:10]

                if due_date_only < today:
                    fee_list.append(data)

            fee_list = self._sort_fees(fee_list)

            logger.info(
                f"Fetched {len(fee_list)} overdue fee records."
            )

            return fee_list

        except Exception:
            logger.exception(
                "Failed to retrieve overdue fee records."
            )
            raise

    def get_fee_statistics(self):
        """
        Aggregate numbers for a dashboard: counts and amounts
        across all active fee records.

        collected_amount = amount + late_fee - discount, for Paid fees.
        pending_amount = remaining_amount (falls back to amount if
        remaining_amount isn't set), for Pending fees.
        """
        try:
            fees = self._fee_query().stream()

            total_fees = 0
            pending_count = 0
            paid_count = 0
            collected_amount = 0.0
            pending_amount = 0.0
            total_late_fee = 0.0

            for fee in fees:
                data = self._fee_to_dict(fee)

                total_fees += 1

                amount = float(data.get("amount", 0) or 0)
                remaining = float(data.get("remaining_amount", 0) or 0)
                late_fee = float(data.get("late_fee", 0) or 0)
                discount = float(data.get("discount", 0) or 0)
                status = data.get("status")

                total_late_fee += late_fee

                if status == "Paid":
                    paid_count += 1
                    collected_amount += (amount + late_fee - discount)
                elif status == "Pending":
                    pending_count += 1
                    pending_amount += remaining if remaining > 0 else amount

            stats = {
                "total_fees": total_fees,
                "pending_count": pending_count,
                "paid_count": paid_count,
                "collected_amount": collected_amount,
                "pending_amount": pending_amount,
                "total_late_fee": total_late_fee,
            }

            logger.info(
                f"Fee statistics computed successfully | {stats}"
            )

            return stats

        except Exception:
            logger.exception(
                "Failed to compute fee statistics."
            )
            raise

    def get_latest_fee(self, student_id: str):
        """
        Most recent fee record for a student, by created_at.
        """
        try:
            student_id = str(student_id).strip().upper()

            fees = (
                self._fee_query()
                .where("student_id", "==", student_id)
                .stream()
            )

            fee_list = [self._fee_to_dict(fee) for fee in fees]

            if not fee_list:
                return None

            fee_list = self._sort_fees(fee_list)

            logger.info(
                f"Latest fee record retrieved successfully | Student ID: {student_id}"
            )

            return fee_list[0]

        except Exception:
            logger.exception(
                "Failed to retrieve latest fee record."
            )
            raise

    def update_fee_record(self, firebase_id: str, fee_data: dict):
        try:
            firebase_id = str(firebase_id).strip()

            fee = self.collection.document(firebase_id).get()

            if not fee.exists:
                return False

            fee_data = self._prepare_update_data(fee_data)

            self.collection.document(firebase_id).update(fee_data)

            logger.info(
                f"Fee record updated successfully | Firebase ID: {firebase_id}"
            )

            return True

        except Exception:
            logger.exception(
                "Failed to update fee record."
            )
            raise

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

            fee = self.collection.document(firebase_id).get()

            if not fee.exists:
                return False

            update_data = {
                "status": "Paid",
                "is_active": True,
                "is_late": False,
                "payment_date": payment_date,
                "payment_method": payment_method,
                "transaction_id": transaction_id,
                "remaining_amount": 0.0,
                "approved_by": approved_by,
                "approved_at": self._timestamp(),
                "updated_at": self._timestamp(),
            }

            if transaction_id:
                update_data["transaction_id"] = transaction_id

            if payment_method:
                update_data["payment_method"] = payment_method

            self.collection.document(firebase_id).update(update_data)

            logger.info(
                f"Fee approved successfully | Firebase ID: {firebase_id}"
            )

            return True

        except Exception:
            logger.exception(
                "Failed to approve fee payment."
            )
            raise

    def search_fee_records(self, keyword: str):
        try:
            keyword = str(keyword).strip().lower()

            if not keyword:
                return []

            fees = self._fee_query().stream()

            result = []

            for fee in fees:
                data = self._fee_to_dict(fee)

                searchable_fields = [
                    str(data.get("receipt_no", "")).lower(),
                    str(data.get("student_id", "")).lower(),
                    str(data.get("student_name", "")).lower(),
                    str(data.get("room_number", "")).lower(),
                    str(data.get("block", "")).lower(),
                    str(data.get("month", "")).lower(),
                    str(data.get("year", "")).lower(),
                    str(data.get("status", "")).lower(),
                    str(data.get("payment_method", "")).lower(),
                    str(data.get("transaction_id", "")).lower(),
                    str(data.get("due_date", "")).lower(),
                    str(data.get("payment_date", "")).lower(),
                    str(data.get("student_firebase_id", "")).lower(),
                ]

                if any(keyword in field for field in searchable_fields):
                    result.append(data)

            result = self._sort_fees(result)

            logger.info(
                f"Fee search completed | Keyword: {keyword} | Results: {len(result)}"
            )

            return result

        except Exception:
            logger.exception(
                "Failed to search fee records."
            )
            raise

    def disable_fee_record(self, firebase_id: str):
        try:
            firebase_id = str(firebase_id).strip()

            fee = self.collection.document(firebase_id).get()

            if not fee.exists:
                return False

            self.collection.document(firebase_id).update(
                {
                    "is_active": False,
                    "updated_at": self._timestamp(),
                }
            )

            logger.info(
                f"Fee record disabled successfully | Firebase ID: {firebase_id}"
            )

            return True

        except Exception:
            logger.exception(
                "Failed to disable fee record."
            )
            raise

    def enable_fee_record(self, firebase_id: str):
        try:
            firebase_id = str(firebase_id).strip()

            fee = self.collection.document(firebase_id).get()

            if not fee.exists:
                return False

            self.collection.document(firebase_id).update(
                {
                    "is_active": True,
                    "updated_at": self._timestamp(),
                }
            )

            logger.info(
                f"Fee record enabled successfully | Firebase ID: {firebase_id}"
            )

            return True

        except Exception:
            logger.exception(
                "Failed to enable fee record."
            )
            raise

    def get_fee_by_student_month_year(
        self,
        student_id: str,
        month: str,
        year: int,
    ):
        try:
            student_id = str(student_id).strip().upper()
            month = str(month).strip()

            fees = (
                self._fee_query()
                .where("student_id", "==", student_id)
                .where("month", "==", month)
                .where("year", "==", year)
                .limit(1)
                .stream()
            )

            for fee in fees:
                data = self._fee_to_dict(fee)

                logger.info(
                    "Fee record retrieved successfully | "
                    f"Student ID: {student_id} | Month: {month} | Year: {year}"
                )

                return data

            return None

        except Exception:
            logger.exception(
                "Failed to retrieve fee record by Student ID, Month, and Year."
            )
            raise

    def fee_exists(
        self,
        student_id: str,
        month: str,
        year: int,
    ):
        try:
            return (
                self.get_fee_by_student_month_year(
                    student_id,
                    month,
                    year,
                )
                is not None
            )

        except Exception:
            logger.exception("Failed to check fee existence.")
            raise