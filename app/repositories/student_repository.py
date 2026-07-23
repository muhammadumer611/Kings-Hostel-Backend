from datetime import datetime, UTC

from app.firebase.firebase import db
from app.utils.logger import logger


class StudentRepository:

    def __init__(self):
        self.collection = db.collection("students")

    def create_student(self, student_data: dict):
        try:
            student_ref = self.collection.document()

            student_data["created_at"] = datetime.now(UTC)
            student_data["updated_at"] = datetime.now(UTC)

            student_ref.set(student_data)

            return student_ref.id

        except Exception:
            logger.exception("Failed to create student")
            raise

    def get_student_by_cnic(self, cnic: str):
        try:
            students = (
                self.collection
                .where("cnic", "==", cnic)
                .limit(1)
                .stream()
            )

            for student in students:
                return student.to_dict()

            return None

        except Exception:
            logger.exception("Failed to fetch student by CNIC")
            raise

    def get_student_by_phone(self, phone: str):
        try:
            students = (
                self.collection
                .where("phone", "==", phone)
                .limit(1)
                .stream()
            )

            for student in students:
                return student.to_dict()

            return None

        except Exception:
            logger.exception("Failed to fetch student by phone")
            raise

    def get_all_students(self):
        try:
            students = self.collection.stream()

            student_list = []

            for student in students:
                data = student.to_dict()
                data["firebase_id"] = student.id
                student_list.append(data)

            return student_list

        except Exception:
            logger.exception("Failed to fetch students")
            raise

    def get_student_by_id(self, student_id: str):
        try:
            student = self.collection.document(student_id).get()

            if not student.exists:
                return None

            data = student.to_dict()
            data["firebase_id"] = student.id

            return data

        except Exception:
            logger.exception("Failed to fetch student by ID")
            raise


    def student_exists(self, student_id: str):
        try:
            student = self.collection.document(student_id).get()
            return student.exists

        except Exception:
            logger.exception("Failed to check student")
            raise

    def count_students(self):
        try:
            return sum(1 for _ in self.collection.stream())

        except Exception:
            logger.exception("Failed to count students")
            raise

    def update_student(
        self,
        student_id: str,
        student_data: dict,
    ):
        try:
            student_data["updated_at"] = datetime.now(UTC)

            self.collection.document(student_id).update(student_data)

            return True

        except Exception:
            logger.exception("Failed to update student")
            raise

    def delete_student(self, student_id: str):
        try:
            self.collection.document(student_id).delete()

            return True

        except Exception:
            logger.exception("Failed to delete student")
            raise

    def search_students(self, keyword: str):
        try:
            keyword = keyword.lower()

            students = self.collection.stream()

            result = []

            for student in students:

                data = student.to_dict()

                name = str(
                    data.get("name", "")
                ).lower()

                cnic = str(
                    data.get("cnic", "")
                ).lower()

                phone = str(
                    data.get("phone", "")
                ).lower()

                if (
                    keyword in name
                    or keyword in cnic
                    or keyword in phone
                ):
                    data["firebase_id"] = student.id
                    result.append(data)

            return result

        except Exception:
            logger.exception("Failed to search students")
            raise