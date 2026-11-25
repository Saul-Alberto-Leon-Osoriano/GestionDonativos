import re

from fastapi import HTTPException

from backend.repositories import RepositorioUsuarios
from backend.schemas import RolUsuario, Usuario, UsuarioActualizar, UsuarioCrear


class ServicioUsuarios:
    """Reglas de negocio y CRUD de usuarios."""

    def __init__(self, repositorio: RepositorioUsuarios) -> None:
        self._repositorio = repositorio

    def listar(self) -> list[Usuario]:
        return self._repositorio.listar()

    def _generar_id(self, rol: RolUsuario, excluir_id: str | None = None) -> str:
        prefijo = "A" if rol == RolUsuario.ADMINISTRATIVO else "U"
        patron = re.compile(rf"^{prefijo}(\d{{3}})$")
        usuarios = self._repositorio.listar()
        ids_ocupados = {u.id for u in usuarios if u.id != excluir_id}

        mayor = 0
        for usuario in usuarios:
            if usuario.id == excluir_id:
                continue
            coincidencia = patron.match(usuario.id)
            if coincidencia:
                mayor = max(mayor, int(coincidencia.group(1)))

        while True:
            mayor += 1
            candidato = f"{prefijo}{mayor:03d}"
            if candidato not in ids_ocupados:
                return candidato

    def crear(self, datos: UsuarioCrear) -> Usuario:
        if self._repositorio.existe_correo(datos.correo):
            raise HTTPException(
                status_code=400, detail="Ya existe un usuario con ese correo."
            )

        usuario = Usuario(
            id=self._generar_id(datos.rol),
            nombre=datos.nombre,
            telefono=datos.telefono,
            correo=datos.correo,
            rol=datos.rol,
            activo=datos.activo,
        )
        return self._repositorio.crear(usuario)

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
        if not cambios:
            return actual

        correo = cambios.get("correo")
        if correo and self._repositorio.existe_correo(correo, excluir_id=id_usuario):
            raise HTTPException(
                status_code=400, detail="Ya existe un usuario con ese correo."
            )

        nuevo_rol = cambios.get("rol")
        if nuevo_rol is not None and nuevo_rol != actual.rol:
            nuevo_id = self._generar_id(nuevo_rol, excluir_id=id_usuario)
            valores = actual.model_dump(by_alias=False)
            valores.update(cambios)
            valores["id"] = nuevo_id
            self._repositorio.eliminar(id_usuario)
            return self._repositorio.crear(Usuario.model_validate(valores))

        actualizado = self._repositorio.actualizar(id_usuario, cambios)
        if actualizado is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return actualizado

    def eliminar(self, id_usuario: str) -> None:
        if not self._repositorio.eliminar(id_usuario):
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
