from collections.abc import Iterable
from copy import deepcopy
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class RepositorioMemoria(Generic[T]):
    """Almacenamiento temporal en memoria, sustituible por otra implementacion."""

    def __init__(self, semilla: Iterable[T] | None = None) -> None:
        self._lista: list[T] = [deepcopy(elemento) for elemento in semilla or []]

    def listar(self) -> list[T]:
        return deepcopy(self._lista)

    def obtener_por_id(self, id_: str) -> T | None:
        for elemento in self._lista:
            if getattr(elemento, "id") == id_:
                return deepcopy(elemento)
        return None

    def crear(self, elemento: T) -> T:
        self._lista.append(deepcopy(elemento))
        return deepcopy(elemento)

    def actualizar(self, id_: str, cambios: dict[str, Any]) -> T | None:
        for indice, elemento in enumerate(self._lista):
            if getattr(elemento, "id") == id_:
                actualizado = elemento.model_copy(update=cambios)
                self._lista[indice] = actualizado
                return deepcopy(actualizado)
        return None

    def eliminar(self, id_: str) -> bool:
        for indice, elemento in enumerate(self._lista):
            if getattr(elemento, "id") == id_:
                del self._lista[indice]
                return True
        return False

    def contar(self) -> int:
        return len(self._lista)
