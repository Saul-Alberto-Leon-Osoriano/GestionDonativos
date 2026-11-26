from .auth import router as router_auth
from .donativos import router as router_donativos
from .entregas import router as router_entregas
from .lotes import router as router_lotes
from .transparencia import router as router_transparencia
from .usuarios import router as router_usuarios

__all__ = [
    "router_auth",
    "router_donativos",
    "router_entregas",
    "router_lotes",
    "router_transparencia",
    "router_usuarios",
]
