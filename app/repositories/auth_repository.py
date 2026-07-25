from firebase_admin import auth

from app.firebase.firebase import db
from app.utils.logger import logger


class AuthRepository:

    def __init__(self):
        self.collection = db.collection("admins")

    def get_admin_by_email(self, email: str):
        try:
            return auth.get_user_by_email(email)

        except Exception:
            logger.exception(
                "Failed to fetch admin by email."
            )
            return None

    def get_admin_profile(self, uid: str):
        try:

            admin = (
                self.collection
                .document(uid)
                .get()
            )

            if not admin.exists:
                return None

            return admin.to_dict()

        except Exception:
            logger.exception(
                "Failed to fetch admin profile."
            )
            raise

    def create_admin(
        self,
        email: str,
        password: str,
    ):

        user = auth.create_user(
            email=email,
            password=password,
        )

        self.collection.document(
            user.uid
        ).set({

            "uid": user.uid,

            "email": email,

            "full_name": "Kings Hostel Admin",

            "phone": "",

            "role": "super_admin",

            "profile_image": "",

            "is_active": True,

            "last_login": None,

            "created_at": None,

            "updated_at": None,
        })

        return user

    def verify_admin(
        self,
        email: str,
    ):
        try:

            user = auth.get_user_by_email(email)

            admin = (
                self.collection
                .document(user.uid)
                .get()
            )

            if not admin.exists:
                return None

            data = admin.to_dict()
            data["uid"] = user.uid

            return data

        except Exception:

            logger.exception(
                "Failed to verify admin."
            )

            return None

    def update_email(
        self,
        uid: str,
        new_email: str,
    ):

        try:

            auth.update_user(
                uid,
                email=new_email,
            )

            self.collection.document(
                uid
            ).update({

                "email": new_email,

            })

            return True

        except Exception:

            logger.exception(
                "Failed to update email."
            )

            raise

    def update_password(
        self,
        uid: str,
        new_password: str,
    ):

        try:

            auth.update_user(
                uid,
                password=new_password,
            )

            return True

        except Exception:

            logger.exception(
                "Failed to update password."
            )

            raise

    def update_last_login(
        self,
        uid: str,
        login_time,
    ):

        try:

            self.collection.document(
                uid
            ).update({

                "last_login": login_time,

            })

            return True

        except Exception:

            logger.exception(
                "Failed to update last login."
            )

            raise