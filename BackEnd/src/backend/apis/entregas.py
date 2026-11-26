from fastapi import APIRouter, Depends

from backend.dependencies import require_admin
from backend.schemas import Entrega, EntregaCrear, Usuario
from backend.services import servicio_entregas

router = APIRouter(
    prefix="/api/entregas",
    tags=["entregas"],
    dependencies=[Depends(require_admin)],
)


@router.post("", response_model=Entrega, status_code=201)
def crear_entrega(
    datos: EntregaCrear,
    admin: Usuario = Depends(require_admin),
) -> Entrega:
    return servicio_entregas.crear(datos, admin.id_usuario or 0)
