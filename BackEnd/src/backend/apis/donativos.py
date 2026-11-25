from fastapi import APIRouter, HTTPException

from backend.schemas import DonativoDraft, Lote
from backend.services import servicio_donativos

router = APIRouter(prefix="/api/donativos", tags=["donativos"])


@router.post("", response_model=Lote, status_code=201)
def registrar_donativo(draft: DonativoDraft) -> Lote:
    try:
        return servicio_donativos.crear_desde_donativo(draft)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al registrar el donativo."
        ) from exc
