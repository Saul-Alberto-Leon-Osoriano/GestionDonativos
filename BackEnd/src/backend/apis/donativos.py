from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import require_admin
from backend.schemas import DonativoDraft, Lote, Usuario
from backend.services import servicio_donativos

router = APIRouter(
    prefix="/api/donativos",
    tags=["donativos"],
    dependencies=[Depends(require_admin)],
)


@router.post("", response_model=Lote, status_code=201)
def registrar_donativo(
    draft: DonativoDraft,
    admin: Usuario = Depends(require_admin),
) -> Lote:
    try:
        return servicio_donativos.crear_desde_donativo(
            draft, admin.id_usuario or 0
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al registrar el donativo."
        ) from exc
