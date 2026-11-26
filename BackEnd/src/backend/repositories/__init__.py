from .entregas import RepositorioEntregas
from .lotes import RepositorioLotes
from .transparencia import RepositorioMetas
from .usuarios import RepositorioUsuarios

repositorio_lotes = RepositorioLotes()
repositorio_usuarios = RepositorioUsuarios()
repositorio_metas = RepositorioMetas()
repositorio_entregas = RepositorioEntregas()

__all__ = [
    "RepositorioEntregas",
    "RepositorioLotes",
    "RepositorioMetas",
    "RepositorioUsuarios",
    "repositorio_entregas",
    "repositorio_lotes",
    "repositorio_metas",
    "repositorio_usuarios",
]
