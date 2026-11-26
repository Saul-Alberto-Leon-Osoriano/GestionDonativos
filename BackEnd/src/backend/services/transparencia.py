from typing import Protocol

from backend.repositories import RepositorioEntregas, RepositorioMetas
from backend.schemas import (
    EstadisticasPublicas,
    HitoDonacion,
    Lote,
    MetaDonacion,
)

from .donativos import redondear


class ProveedorLotes(Protocol):
    def listar(self) -> list[Lote]: ...


class ServicioTransparencia:
    """Metas, hitos y estadisticas publicas."""

    def __init__(
        self,
        repositorio_metas: RepositorioMetas,
        repositorio_entregas: RepositorioEntregas,
        proveedor_lotes: ProveedorLotes,
    ) -> None:
        self._repositorio_metas = repositorio_metas
        self._repositorio_entregas = repositorio_entregas
        self._proveedor_lotes = proveedor_lotes

    def metas(self) -> list[MetaDonacion]:
        recolectado = self._repositorio_metas.recolectado_por_categoria()
        return [
            MetaDonacion(
                **meta.model_dump(by_alias=False),
                recolectado_kg=redondear(recolectado.get(meta.categoria, 0)),
            )
            for meta in self._repositorio_metas.listar()
        ]

    def hitos(self) -> list[HitoDonacion]:
        return self._repositorio_entregas.listar_hitos()

    def estadisticas(self) -> EstadisticasPublicas:
        lotes = self._proveedor_lotes.listar()
        return EstadisticasPublicas(
            total_kg=redondear(sum(lote.volumen for lote in lotes)),
            total_lotes=len(lotes),
            total_familias=sum(lote.familias_beneficiadas for lote in lotes),
        )
