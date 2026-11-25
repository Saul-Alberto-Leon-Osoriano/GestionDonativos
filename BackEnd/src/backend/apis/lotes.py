from fastapi import APIRouter, HTTPException, Query, Response

from backend.schemas import (
    AlertaVencimiento,
    EstadoLote,
    KpisInventario,
    Lote,
    LoteCrear,
    LoteEstadoActualizar,
    RespuestaPaginada,
)
from backend.services import servicio_lotes

router = APIRouter(prefix="/api/lotes", tags=["lotes"])


@router.get("", response_model=RespuestaPaginada[Lote])
def listar_lotes(
    termino: str | None = None,
    estado: EstadoLote | None = None,
    categoria: str | None = None,
    pagina: int = Query(1, ge=1),
    tamano_pagina: int = Query(20, ge=1, le=100, alias="tamanoPagina"),
) -> RespuestaPaginada[Lote]:
    try:
        return servicio_lotes.listar_paginado(
            termino, estado, categoria, pagina, tamano_pagina
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al listar los lotes."
        ) from exc


@router.get("/alertas", response_model=list[AlertaVencimiento])
def obtener_alertas() -> list[AlertaVencimiento]:
    try:
        return servicio_lotes.alertas()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al obtener las alertas."
        ) from exc


@router.get("/kpis", response_model=KpisInventario)
def obtener_kpis() -> KpisInventario:
    try:
        return servicio_lotes.kpis()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al obtener los KPIs."
        ) from exc


@router.get("/exportar.csv", response_class=Response)
def exportar_lotes_csv(
    termino: str | None = None,
    estado: EstadoLote | None = None,
    categoria: str | None = None,
) -> Response:
    try:
        contenido = servicio_lotes.exportar_csv(termino, estado, categoria)
        return Response(
            content=contenido,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="lotes.csv"'},
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al exportar los lotes."
        ) from exc


@router.get("/{id_lote}", response_model=Lote)
def obtener_lote(id_lote: str) -> Lote:
    try:
        return servicio_lotes.obtener(id_lote)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al obtener el lote."
        ) from exc


@router.post("", response_model=Lote, status_code=201)
def crear_lote(datos: LoteCrear) -> Lote:
    try:
        return servicio_lotes.crear(datos)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al crear el lote."
        ) from exc


@router.put("/{id_lote}/estado", response_model=Lote)
def cambiar_estado_lote(id_lote: str, datos: LoteEstadoActualizar) -> Lote:
    try:
        return servicio_lotes.cambiar_estado(id_lote, datos.estado)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al cambiar el estado del lote."
        ) from exc
