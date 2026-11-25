from backend.schemas import Usuario

from .base import RepositorioMemoria
from .semilla import _USUARIOS_SEMILLA


class RepositorioUsuarios(RepositorioMemoria[Usuario]):
    def __init__(self) -> None:
        super().__init__(_USUARIOS_SEMILLA)

    def obtener_por_correo(self, correo: str) -> Usuario | None:
        correo_normalizado = correo.casefold()
        for usuario in self._lista:
            if usuario.correo.casefold() == correo_normalizado:
                return usuario.model_copy(deep=True)
        return None

    def existe_correo(self, correo: str, excluir_id: str | None = None) -> bool:
        usuario = self.obtener_por_correo(correo)
        return usuario is not None and usuario.id != excluir_id
