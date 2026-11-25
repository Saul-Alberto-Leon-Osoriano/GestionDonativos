from backend.repositories import (
    repositorio_entregas,
    repositorio_lotes,
    repositorio_metas,
    repositorio_usuarios,
)

from .auth import ServicioAuth
from .donativos import ServicioDonativos
from .entregas import ServicioEntregas
from .lotes import ServicioLotes
from .transparencia import ServicioTransparencia
from .usuarios import ServicioUsuarios

servicio_lotes = ServicioLotes(repositorio_lotes)
servicio_donativos = ServicioDonativos(servicio_lotes)
servicio_usuarios = ServicioUsuarios(repositorio_usuarios)
servicio_auth = ServicioAuth(repositorio_usuarios)
servicio_entregas = ServicioEntregas(repositorio_entregas)
servicio_transparencia = ServicioTransparencia(
    repositorio_metas,
    repositorio_entregas,
    servicio_lotes,
)

__all__ = [
    "ServicioAuth",
    "ServicioDonativos",
    "ServicioEntregas",
    "ServicioLotes",
    "ServicioTransparencia",
    "ServicioUsuarios",
    "servicio_auth",
    "servicio_donativos",
    "servicio_entregas",
    "servicio_lotes",
    "servicio_transparencia",
    "servicio_usuarios",
]
