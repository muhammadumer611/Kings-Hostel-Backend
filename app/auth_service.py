from firebase_admin import auth
from app.firebase.firebase import db


class AuthService:

    @staticmethod
    def create_default_admin(email, password):

        user = auth.create_user(
            email=email,
            password=password
        )

        db.collection("admins").document(user.uid).set({
            "uid": user.uid,
            "full_name": "Kings Hostel Admin",
            "email": email,
            "role": "super_admin",
            "is_active": True
        })

        return user