"""Adaptadores de seguridad: hashing (bcrypt) y tokens (JWT)."""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.domain.ports import PasswordHasher, TokenService

# Clave única de este proyecto. En producción, defínela como variable de
# entorno SECRET_KEY para poder rotarla sin tocar el código.
_SECRET = os.environ.get("SECRET_KEY", "-WMZZzEa9YMKP1gOUgsp9DM4Bp5slLLxH9KUf1G9vc5c2KS0bYMYpgxBD4gQtNVB")
_ALGO = "HS256"
_EXPIRE_MIN = 60 * 24


class BcryptHasher(PasswordHasher):
    def __init__(self) -> None:
        self._ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, plain: str) -> str:
        return self._ctx.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return self._ctx.verify(plain, hashed)


class JwtTokenService(TokenService):
    def issue(self, username: str) -> str:
        payload = {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=_EXPIRE_MIN)}
        return jwt.encode(payload, _SECRET, algorithm=_ALGO)

    def username_from(self, token: str) -> str | None:
        try:
            return jwt.decode(token, _SECRET, algorithms=[_ALGO]).get("sub")
        except JWTError:
            return None
