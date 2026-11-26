"""Pruebas de seguridad que no requieren conexion a MySQL."""

import pytest

from backend.schemas import RolUsuario, Usuario
from backend.security import (
    crear_token,
    decodificar_token,
    hash_password,
    verify_password,
)


def _usuario() -> Usuario:
    return Usuario(
        id="A001",
        id_usuario=1,
        nombre="Prof. Taipe",
        telefono="+51 999 999 999",
        correo="pastoral@sanpiox.edu.pe",
        rol=RolUsuario.ADMINISTRATIVO,
        activo=True,
    )


def test_hash_argon2_verifica_password() -> None:
    password_hash = hash_password("admin123")

    assert password_hash.startswith("$argon2")
    assert verify_password(password_hash, "admin123")
    assert not verify_password(password_hash, "otra-clave")


def test_jwt_contiene_sub_y_rol() -> None:
    token = crear_token(_usuario())
    payload = decodificar_token(token)

    assert payload["sub"] == "A001"
    assert payload["rol"] == "administrativo"


def test_jwt_invalido_lanza_error() -> None:
    with pytest.raises(ValueError):
        decodificar_token("token.invalido.firma")
