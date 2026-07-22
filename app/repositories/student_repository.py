from datetime import datetime
from app.firebase.firebase import db


class StudentRepository:

    def create_student(self, student_data: dict):
        try:
            student_ref = db.collection("students").document()

            student_data["created_at"] = datetime.utcnow()
            student_data["updated_at"] = datetime.utcnow()

            student_ref.set(student_data)

            return student_ref.id

        except Exception as e:
            raise Exception(f"Failed to create student: {str(e)}")

    def get_student_by_cnic(self, cnic: str):
        try:
            students = (
                db.collection("students")
                .where("cnic", "==", cnic)
                .limit(1)
                .stream()
            )

            for student in students:
                return student.to_dict()

            return None

        except Exception as e:
            raise Exception(f"Failed to fetch student by CNIC: {str(e)}")

    def get_student_by_phone(self, phone: str):
        try:
            students = (
                db.collection("students")
                .where("phone", "==", phone)
                .limit(1)
                .stream()
            )

            for student in students:
                return student.to_dict()

            return None

        except Exception as e:
            raise Exception(f"Failed to fetch student by phone: {str(e)}")

    def get_all_students(self):
        try:
            students = db.collection("students").stream()

            student_list = []

            for student in students:
                data = student.to_dict()
                data["firebase_id"] = student.id
                student_list.append(data)

            return student_list

        except Exception as e:
            raise Exception(f"Failed to fetch students: {str(e)}")

    def get_student_by_id(self, student_id: str):
        try:
            student_ref = db.collection("students").document(student_id)
            student = student_ref.get()

            if not student.exists:
                return None

            data = student.to_dict()
            data["firebase_id"] = student.id

            return data

        except Exception as e:
            raise Exception(f"Failed to fetch student by ID: {str(e)}")