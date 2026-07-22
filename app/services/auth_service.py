from app.repositories.auth_repository import AuthRepository


class AuthService:

    def __init__(self):
        self.repository = AuthRepository()

    def create_default_admin(self, email, password):

        admin = self.repository.get_admin_by_email(email)

        if admin:
            return "Admin already exists."

        self.repository.create_admin(email, password)

        return "Admin created successfully."