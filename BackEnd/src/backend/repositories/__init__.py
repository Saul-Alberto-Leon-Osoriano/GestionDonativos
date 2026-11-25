from .lotes import RepositorioLotes
from .transparencia import RepositorioMetas
from .usuarios import RepositorioUsuarios

repositorio_lotes = RepositorioLotes()
repositorio_usuarios = RepositorioUsuarios()
repositorio_metas = RepositorioMetas()

__all__ = [
    "RepositorioLotes",
    "RepositorioMetas",
    "RepositorioUsuarios",
    "repositorio_lotes",
    "repositorio_metas",
    "repositorio_usuarios",
]
