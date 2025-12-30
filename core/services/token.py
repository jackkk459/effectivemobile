from datetime import timedelta
from typing import Optional

import jwt
from django.conf import settings
from django.utils import timezone

from core.models import User


def generate_token(user: User) -> str:
    payload = {
        "user_id": user.id,
        "token_version": user.token_version,
        "exp": timezone.now() + timedelta(hours=24),
        "iat": timezone.now(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

    user_id = payload.get("user_id")
    token_version = payload.get("token_version")

    if not user_id:
        return None

    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return None

    if user.token_version != token_version:
        return None

    return user
