from typing import Protocol

from backend.repositories import RepositorioMetas
from backend.schemas import (
    EstadoHito,
    EstadoLote,
    EstadisticasPublicas,
    HitoDonacion,
    Lote,
    MetaDonacion,
)

from .donativos import redondear


class ProveedorLotes(Protocol):
    def listar(self) -> list[Lote]: ...


class ServicioTransparencia:
    """Metas, hitos y estadisticas publicas derivadas de los lotes."""

    def __init__(
        self, repositorio_metas: RepositorioMetas, proveedor_lotes: ProveedorLotes
    ) -> None:
        self._repositorio_metas = repositorio_metas
        self._proveedor_lotes = proveedor_lotes

    def metas(self) -> list[MetaDonacion]:
        lotes = self._proveedor_lotes.listar()
        resultado: list[MetaDonacion] = []
        for meta in self._repositorio_metas.listar():
            recolectado = redondear(
                sum(
                    lote.volumen
                    for lote in lotes
                    if lote.categoria_principal == meta.categoria
                )
            )
            resultado.append(
                MetaDonacion(
                    **meta.model_dump(by_alias=False), recolectado_kg=recolectado
                )
            )
        return resultado

    def hitos(self) -> list[HitoDonacion]:
        lotes = sorted(
            self._proveedor_lotes.listar(), key=lambda lote: lote.fecha_ingreso
        )
        hitos: list[HitoDonacion] = []
        for indice, lote in enumerate(lotes, start=1):
            entregado = lote.estado == EstadoLote.ENTREGADO
            estado = EstadoHito.RECEPCIONADO if entregado else EstadoHito.PREPARACION
            sufijo = lote.codigo.rsplit("-", 1)[-1]
            hitos.append(
                HitoDonacion(
                    id=f"hito-{indice:03d}",
                    fecha=lote.fecha_ingreso,
                    lote=lote.codigo,
                    titulo=(
                        f"Lote {lote.codigo} entregado"
                        if entregado
                        else f"Lote {lote.codigo} en preparacion"
                    ),
                    descripcion=lote.descripcion,
                    receptor=lote.destino,
                    acta=f"ACTA-{sufijo}",
                    estado=estado,
                )
            )
        return hitos

    def estadisticas(self) -> EstadisticasPublicas:
        lotes = self._proveedor_lotes.listar()
        return EstadisticasPublicas(
            total_kg=redondear(sum(lote.volumen for lote in lotes)),
            total_lotes=len(lotes),
            total_familias=sum(lote.familias_beneficiadas for lote in lotes),
        )
