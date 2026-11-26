"""Hash Argon2 y emision/validacion de JWT."""

from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from .config import obtener_settings
from .schemas import Usuario

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def password_necesita_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return True


def crear_token(usuario: Usuario) -> str:
    settings = obtener_settings()
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": usuario.id,
        "rol": usuario.rol.value,
        "nombre": usuario.nombre,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=settings.jwt_expiration_minutes),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decodificar_token(token: str) -> dict[str, object]:
    settings = obtener_settings()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.InvalidTokenError as exc:
        raise ValueError("Token invalido o expirado.") from exc
