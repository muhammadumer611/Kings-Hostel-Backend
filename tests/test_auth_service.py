from app.services import auth_service as auth_service_module
from app.services.auth_service import AuthService


def test_login_returns_token_for_valid_admin_credentials(monkeypatch):
    monkeypatch.setattr(auth_service_module.settings, "ADMIN_EMAIL", "admin@example.com", raising=False)
    monkeypatch.setattr(auth_service_module.settings, "ADMIN_PASSWORD", "secret123", raising=False)

    service = AuthService()
    result = service.authenticate_admin("admin@example.com", "secret123")

    assert result["success"] is True
    assert result["message"] == "Login successful."
    assert result["data"]["access_token"]
    assert result["data"]["token_type"] == "bearer"


def test_login_rejects_invalid_admin_credentials(monkeypatch):
    monkeypatch.setattr(auth_service_module.settings, "ADMIN_EMAIL", "admin@example.com", raising=False)
    monkeypatch.setattr(auth_service_module.settings, "ADMIN_PASSWORD", "secret123", raising=False)

    service = AuthService()
    result = service.authenticate_admin("admin@example.com", "wrong-password")

    assert result["success"] is False
    assert result["message"] == "Invalid email or password."
    assert result["data"] is None
