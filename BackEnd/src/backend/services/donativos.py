from collections import Counter
from typing import Protocol

from fastapi import HTTPException

from backend.schemas import (
    ArticuloDonacion,
    DonativoDraft,
    Lote,
)

from .fechas import dias_hasta


class CreadorLotes(Protocol):
    def crear_desde_donativo(
        self, draft: DonativoDraft, id_agente_pastoral: int
    ) -> Lote: ...


def redondear(valor: float) -> float:
    return round(valor + 0.0, 2)


def calcular_peso_neto(articulos: list[ArticuloDonacion]) -> float:
    return redondear(
        sum(
            articulo.cantidad * (articulo.peso_unitario_kg or 0)
            for articulo in articulos
        )
    )


def calcular_resumen(draft: DonativoDraft):
    por_vencer = 0
    for articulo in draft.articulos:
        if articulo.fecha_vencimiento is None:
            continue
        dias = dias_hasta(articulo.fecha_vencimiento)
        if 0 <= dias <= 30:
            por_vencer += 1

    return {
        "total_articulos": len(draft.articulos),
        "total_unidades": redondear(sum(a.cantidad for a in draft.articulos)),
        "peso_neto_kg": calcular_peso_neto(draft.articulos),
        "articulos_por_vencer": por_vencer,
    }


def categoria_principal(articulos: list[ArticuloDonacion]) -> str:
    categorias = [
        articulo.categoria.strip()
        for articulo in articulos
        if articulo.categoria and articulo.categoria.strip()
    ]
    if not categorias:
        return "Otros"
    return Counter(categorias).most_common(1)[0][0]


def descripcion_lote(draft: DonativoDraft) -> str:
    descripciones = [
        articulo.descripcion.strip()
        for articulo in draft.articulos
        if articulo.descripcion and articulo.descripcion.strip()
    ]
    descripcion = " | ".join(descripciones) or categoria_principal(draft.articulos)
    if draft.observaciones and draft.observaciones.strip():
        descripcion = f"{descripcion} | {draft.observaciones.strip()}"
    return descripcion


class ServicioDonativos:
    """Convierte el borrador de donativo en un lote pendiente."""

    def __init__(self, creador_lotes: CreadorLotes) -> None:
        self._creador_lotes = creador_lotes

    def crear_desde_donativo(
        self, draft: DonativoDraft, id_agente_pastoral: int
    ) -> Lote:
        if not draft.destino or not draft.destino.strip():
            raise HTTPException(
                status_code=400,
                detail="El destino del donativo es obligatorio.",
            )

        return self._creador_lotes.crear_desde_donativo(
            draft, id_agente_pastoral
        )
