from pydantic import Field

from .base import SchemaBase
from .catalogos import RolUsuario


class Usuario(SchemaBase):
    id: str
    nombre: str
    telefono: str
    correo: str
    rol: RolUsuario
    activo: bool


class UsuarioCrear(SchemaBase):
    nombre: str = Field(min_length=1)
    telefono: str = Field(min_length=1)
    correo: str = Field(min_length=1)
    rol: RolUsuario = RolUsuario.DONANTE
    activo: bool = True


class UsuarioActualizar(SchemaBase):
    nombre: str | None = Field(default=None, min_length=1)
    telefono: str | None = Field(default=None, min_length=1)
    correo: str | None = Field(default=None, min_length=1)
    rol: RolUsuario | None = None
    activo: bool | None = None
