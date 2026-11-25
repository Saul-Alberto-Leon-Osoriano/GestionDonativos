from fastapi import APIRouter, HTTPException

from backend.schemas import EstadisticasPublicas, HitoDonacion, MetaDonacion
from backend.services import servicio_transparencia

router = APIRouter(prefix="/api/transparencia", tags=["transparencia"])


@router.get("/metas", response_model=list[MetaDonacion])
def obtener_metas() -> list[MetaDonacion]:
    try:
        return servicio_transparencia.metas()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al obtener las metas."
        ) from exc


@router.get("/hitos", response_model=list[HitoDonacion])
def obtener_hitos() -> list[HitoDonacion]:
    try:
        return servicio_transparencia.hitos()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al obtener los hitos."
        ) from exc


@router.get("/estadisticas", response_model=EstadisticasPublicas)
def obtener_estadisticas() -> EstadisticasPublicas:
    try:
        return servicio_transparencia.estadisticas()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al obtener las estadisticas."
        ) from exc
