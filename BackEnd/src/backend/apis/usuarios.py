from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import require_admin
from backend.schemas import Usuario, UsuarioActualizar, UsuarioCrear
from backend.services import servicio_usuarios

router = APIRouter(
    prefix="/api/usuarios",
    tags=["usuarios"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[Usuario])
def listar_usuarios() -> list[Usuario]:
    try:
        return servicio_usuarios.listar()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al listar los usuarios."
        ) from exc


@router.post("", response_model=Usuario, status_code=201)
def crear_usuario(
    datos: UsuarioCrear,
    admin: Usuario = Depends(require_admin),
) -> Usuario:
    try:
        return servicio_usuarios.crear(datos, admin)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al crear el usuario."
        ) from exc


@router.put("/{id_usuario}", response_model=Usuario)
def actualizar_usuario(
    id_usuario: str, datos: UsuarioActualizar
) -> Usuario:
    try:
        return servicio_usuarios.actualizar(id_usuario, datos)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al actualizar el usuario."
        ) from exc


@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: str) -> dict[str, str]:
    try:
        servicio_usuarios.eliminar(id_usuario)
        return {"detail": "Usuario desactivado."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Error inesperado al eliminar el usuario."
        ) from exc
