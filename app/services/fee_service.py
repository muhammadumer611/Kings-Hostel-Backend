from app.repositories.fee_repository import FeeRepository


class FeeService:
    def __init__(self):
        self.repository = FeeRepository()

    def create_fee_record(self, fee_data: dict):
        firebase_id = self.repository.create_fee_record(fee_data)
        return {
            "success": True,
            "message": "Fee record created successfully.",
            "data": {"firebase_id": firebase_id},
            "errors": None,
        }

    def get_all_fee_records(self):
        fees = self.repository.get_all_fee_records()
        return {
            "success": True,
            "message": "Fee records retrieved successfully.",
            "data": {"feeRecords": fees},
            "errors": None,
        }
