from backend.repositories import (
    repositorio_lotes,
    repositorio_metas,
    repositorio_usuarios,
)

from .donativos import ServicioDonativos
from .lotes import ServicioLotes
from .transparencia import ServicioTransparencia
from .usuarios import ServicioUsuarios

servicio_lotes = ServicioLotes(repositorio_lotes)
servicio_donativos = ServicioDonativos(servicio_lotes)
servicio_usuarios = ServicioUsuarios(repositorio_usuarios)
servicio_transparencia = ServicioTransparencia(repositorio_metas, servicio_lotes)

__all__ = [
    "ServicioDonativos",
    "ServicioLotes",
    "ServicioTransparencia",
    "ServicioUsuarios",
    "servicio_donativos",
    "servicio_lotes",
    "servicio_transparencia",
    "servicio_usuarios",
]
