from pydantic import Field

from .base import SchemaBase
from .usuario import Usuario


class LoginRequest(SchemaBase):
    correo: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(SchemaBase):
    access_token: str
    token_type: str = "Bearer"
    expira_en: int
    usuario: Usuario


class RecuperacionRequest(SchemaBase):
    correo: str = Field(min_length=1)


class MensajeRespuesta(SchemaBase):
    detail: str
