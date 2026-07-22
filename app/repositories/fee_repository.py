from app.firebase.firebase import db


class FeeRepository:
    def create_fee_record(self, fee_data: dict):
        fee_ref = db.collection("fees").document()
        fee_ref.set(fee_data)
        return fee_ref.id

    def get_all_fee_records(self):
        fees = db.collection("fees").stream()
        result = []
        for fee in fees:
            data = fee.to_dict()
            data["firebase_id"] = fee.id
            result.append(data)
        return result
