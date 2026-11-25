"""Autenticacion con Argon2 y emision de JWT."""

from fastapi import HTTPException, status

from backend.config import obtener_settings
from backend.repositories import RepositorioUsuarios
from backend.repositories.usuarios import CredencialesUsuario
from backend.security import (
    crear_token,
    hash_password,
    password_necesita_rehash,
    verify_password,
)
from backend.schemas import (
    LoginRequest,
    TokenResponse,
    Usuario,
)


class ServicioAuth:
    def __init__(self, repositorio: RepositorioUsuarios) -> None:
        self._repositorio = repositorio

    def _a_usuario(self, credenciales: CredencialesUsuario) -> Usuario:
        return Usuario(
            id=credenciales.codigo_usuario,
            id_usuario=credenciales.id_usuario,
            nombre=credenciales.nombre_completo,
            telefono=credenciales.telefono or "",
            correo=credenciales.correo_electronico,
            rol=credenciales.rol,
            activo=credenciales.activo,
        )

    def login(self, datos: LoginRequest) -> TokenResponse:
        credenciales = self._repositorio.obtener_credenciales(datos.correo)
        if credenciales is None or not credenciales.activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales invalidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(credenciales.password_hash, datos.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales invalidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if password_necesita_rehash(credenciales.password_hash):
            self._repositorio.actualizar(
                credenciales.codigo_usuario,
                {"password_hash": hash_password(datos.password)},
            )

        usuario = self._a_usuario(credenciales)
        token = crear_token(usuario)
        settings = obtener_settings()
        return TokenResponse(
            access_token=token,
            expira_en=settings.jwt_expiration_minutes * 60,
            usuario=usuario,
        )

    def registrar_recuperacion(self, correo: str) -> None:
        self._repositorio.registrar_solicitud_recuperacion(correo)
