from typing import Optional

import bcrypt
from django.utils import timezone

from core.models import User
from core.services.token import generate_token


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def register_user(**data) -> User:
    password = data.pop("password")
    user = User(**data)
    user.password_hash = hash_password(password)
    user.save()
    return user


def login_user(email: str, password: str) -> Optional[str]:
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return None

    if not check_password(password, user.password_hash):
        return None

    return generate_token(user)


def logout_user(user: User) -> None:
    user.token_version += 1
    user.save(update_fields=["token_version"])


def soft_delete_user(user: User) -> None:
    user.is_active = False
    user.deleted_at = timezone.now()
    user.token_version += 1
    user.save()
