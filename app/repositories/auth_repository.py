from firebase_admin import auth
from app.firebase.firebase import db


class AuthRepository:

    def get_admin_by_email(self, email: str):
        try:
            return auth.get_user_by_email(email)
        except:
            return None

    def create_admin(self, email: str, password: str):

        user = auth.create_user(
            email=email,
            password=password
        )

        db.collection("admins").document(user.uid).set({
            "uid": user.uid,
            "email": email,
            "full_name": "Kings Hostel Admin",
            "role": "super_admin",
            "is_active": True
        })

        return user