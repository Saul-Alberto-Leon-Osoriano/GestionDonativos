from backend.schemas import Lote

from .base import RepositorioMemoria
from .semilla import _LOTES_SEMILLA


class RepositorioLotes(RepositorioMemoria[Lote]):
    def __init__(self) -> None:
        super().__init__(_LOTES_SEMILLA)
