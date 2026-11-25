from fastapi import APIRouter, Depends, status

from backend.dependencies import get_current_user
from backend.schemas import (
    LoginRequest,
    MensajeRespuesta,
    RecuperacionRequest,
    TokenResponse,
    Usuario,
)
from backend.services import servicio_auth

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest) -> TokenResponse:
    return servicio_auth.login(datos)


@router.get("/sesion", response_model=Usuario)
def obtener_sesion(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    return usuario


@router.post("/logout", response_model=MensajeRespuesta)
def logout(_: Usuario = Depends(get_current_user)) -> MensajeRespuesta:
    return MensajeRespuesta(detail="Sesion cerrada.")


@router.post(
    "/recuperacion",
    response_model=MensajeRespuesta,
    status_code=status.HTTP_202_ACCEPTED,
)
def solicitar_recuperacion(datos: RecuperacionRequest) -> MensajeRespuesta:
    servicio_auth.registrar_recuperacion(datos.correo)
    return MensajeRespuesta(
        detail="Solicitud registrada. El administrador revisara tu caso."
    )
