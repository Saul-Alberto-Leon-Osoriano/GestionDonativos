from pydantic import Field

from .base import SchemaBase
from .catalogos import RolUsuario


class Usuario(SchemaBase):
    id: str
    id_usuario: int | None = Field(default=None, exclude=True)
    nombre: str
    telefono: str
    correo: str
    rol: RolUsuario
    activo: bool


class UsuarioCrear(SchemaBase):
    nombre: str = Field(min_length=1)
    telefono: str = Field(min_length=1)
    correo: str = Field(min_length=1)
    password: str = Field(min_length=8)
    rol: RolUsuario = RolUsuario.DONANTE
    activo: bool = True


class UsuarioActualizar(SchemaBase):
    nombre: str | None = Field(default=None, min_length=1)
    telefono: str | None = Field(default=None, min_length=1)
    correo: str | None = Field(default=None, min_length=1)
    password: str | None = Field(default=None, min_length=8)
    rol: RolUsuario | None = None
    activo: bool | None = None
