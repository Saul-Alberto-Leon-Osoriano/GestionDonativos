"""Registro de actas de entrega."""

from fastapi import HTTPException

from backend.repositories import RepositorioEntregas
from backend.schemas import Entrega, EntregaCrear


class ServicioEntregas:
    def __init__(self, repositorio: RepositorioEntregas) -> None:
        self._repositorio = repositorio

    def crear(self, datos: EntregaCrear, id_agente_registra: int) -> Entrega:
        try:
            return self._repositorio.crear(datos, id_agente_registra)
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail="No se pudo registrar el acta de entrega.",
            ) from exc
