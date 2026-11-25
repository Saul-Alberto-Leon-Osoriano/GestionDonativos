from backend.schemas import MetaDonacionBase

from .base import RepositorioMemoria
from .semilla import _METAS_BASE_SEMILLA


class RepositorioMetas(RepositorioMemoria[MetaDonacionBase]):
    def __init__(self) -> None:
        super().__init__(_METAS_BASE_SEMILLA)
