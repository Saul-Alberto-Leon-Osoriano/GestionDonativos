"""Reglas de negocio del CRUD de usuarios."""

from fastapi import HTTPException

from backend.repositories import RepositorioUsuarios
from backend.security import hash_password
from backend.schemas import RolUsuario, Usuario, UsuarioActualizar, UsuarioCrear


class ServicioUsuarios:
    """Reglas de negocio y CRUD de usuarios."""

    def __init__(self, repositorio: RepositorioUsuarios) -> None:
        self._repositorio = repositorio

    def listar(self) -> list[Usuario]:
        return self._repositorio.listar()

    def crear(
        self,
        datos: UsuarioCrear,
        creado_por: Usuario | None = None,
    ) -> Usuario:
        if self._repositorio.existe_correo(datos.correo):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un usuario con ese correo.",
            )

        creado_por_id = creado_por.id_usuario if creado_por else None
        return self._repositorio.crear(
            datos,
            password_hash=hash_password(datos.password),
            creado_por_id=creado_por_id,
        )

    def actualizar(self, id_usuario: str, datos: UsuarioActualizar) -> Usuario:
        actual = self._repositorio.obtener_por_id(id_usuario)
        if actual is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        cambios = {
            clave: valor
            for clave, valor in datos.model_dump(
                exclude_unset=True, by_alias=False
            ).items()
            if valor is not None
        }

        password = cambios.pop("password", None)
        if isinstance(password, str) and password.strip():
            cambios["password_hash"] = hash_password(password)

        if not cambios:
            return actual

        correo = cambios.get("correo")
        if correo and self._repositorio.existe_correo(
            str(correo), excluir_id=id_usuario
        ):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un usuario con ese correo.",
            )

        nuevo_rol = cambios.get("rol")
        if nuevo_rol is not None and nuevo_rol != actual.rol:
            rol_enum = (
                nuevo_rol
                if isinstance(nuevo_rol, RolUsuario)
                else RolUsuario(str(nuevo_rol))
            )
            cambios["rol"] = rol_enum
            cambios["codigo_usuario"] = self._repositorio.siguiente_codigo(
                rol_enum
            )

        actualizado = self._repositorio.actualizar(id_usuario, cambios)
        if actualizado is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return actualizado

    def eliminar(self, id_usuario: str) -> None:
        if not self._repositorio.eliminar(id_usuario):
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
