from typing import Any


class APIResponse:

    @staticmethod
    def success(message: str, data: Any = None):
        return {
            "success": True,
            "message": message,
            "data": data,
            "errors": None
        }

    @staticmethod
    def error(message: str, errors: Any = None):
        return {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors
        }