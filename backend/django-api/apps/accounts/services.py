from __future__ import annotations

from django.contrib.auth import authenticate
from django.core import signing


class AuthService:
    @staticmethod
    def authenticate_user(username: str, password: str) -> dict | None:
        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            return None

        token = signing.dumps({"user_id": user.id, "username": user.username}, salt="heart-disease-auth")
        return {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": "admin" if user.is_staff else "user",
                "nickname": user.get_full_name() or user.username,
            },
        }
