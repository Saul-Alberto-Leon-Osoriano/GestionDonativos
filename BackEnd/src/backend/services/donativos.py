from collections import Counter
from typing import Protocol

from fastapi import HTTPException

from backend.schemas import (
    ArticuloDonacion,
    DonativoDraft,
    EstadoLote,
    Lote,
    LoteCrear,
    ResumenDonativo,
    UnidadMedida,
)

from .fechas import dias_hasta, normalizar_utc, utc_actual


class CreadorLotes(Protocol):
    def crear(self, datos: LoteCrear) -> Lote: ...


def redondear(valor: float) -> float:
    return round(valor + 0.0, 2)


def calcular_peso_neto(articulos: list[ArticuloDonacion]) -> float:
    return redondear(
        sum(
            articulo.cantidad * (articulo.peso_unitario_kg or 0)
            for articulo in articulos
        )
    )


def calcular_resumen(draft: DonativoDraft) -> ResumenDonativo:
    por_vencer = 0
    for articulo in draft.articulos:
        if articulo.fecha_vencimiento is None:
            continue
        dias = dias_hasta(articulo.fecha_vencimiento)
        if 0 <= dias <= 30:
            por_vencer += 1

    return ResumenDonativo(
        total_articulos=len(draft.articulos),
        total_unidades=redondear(sum(a.cantidad for a in draft.articulos)),
        peso_neto_kg=calcular_peso_neto(draft.articulos),
        articulos_por_vencer=por_vencer,
    )


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

    def crear_desde_donativo(self, draft: DonativoDraft) -> Lote:
        if not draft.destino or not draft.destino.strip():
            raise HTTPException(
                status_code=400, detail="El destino del donativo es obligatorio."
            )

        resumen = calcular_resumen(draft)
        descripcion = f"{descripcion_lote(draft)} | Peso neto: {resumen.peso_neto_kg:.2f} kg"
        datos = LoteCrear(
            fecha_ingreso=normalizar_utc(utc_actual()),
            categoria_principal=categoria_principal(draft.articulos),
            descripcion=descripcion,
            unidad=UnidadMedida.KG,
            destino=draft.destino.strip(),
            estado=EstadoLote.PENDIENTE,
            familias_beneficiadas=0,
            articulos=draft.articulos,
        )
        return self._creador_lotes.crear(datos)
