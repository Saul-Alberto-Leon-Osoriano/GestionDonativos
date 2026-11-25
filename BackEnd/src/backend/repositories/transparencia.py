"""Repositorio de metas y agregados del Portal de Transparencia."""

import re

from backend.database import conexion
from backend.schemas import MetaDonacionBase

_ESTILOS: dict[str, tuple[str, str]] = {
    "Arroz, Avena y Menestras": ("bi-flower1", "naranjaoscuro"),
    "Conservas de Pescado & Aceites": ("bi-tsunami", "azuloscuro"),
    "Leche evaporada y Suplementos de bebé": (
        "bi-person-arms-up",
        "verdeoscuro",
    ),
    "Fideos y Sémolas Diversas": ("bi-cup-hot-fill", "moradooscuro"),
    "Galletas y Cereales": ("bi-cookie", "naranjaoscuro"),
    "Menestras y Granos": ("bi-basket-fill", "verdeoscuro"),
    "Lácteos y Harinas": ("bi-cup-straw", "azuloscuro"),
    "Otros": ("bi-box-seam-fill", "azuloscuro"),
}


def _slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", texto.casefold()).strip("-")


class RepositorioMetas:
    """Categorias de viveres y lo recolectado por categoria."""

    def listar(self) -> list[MetaDonacionBase]:
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT id_categoria, nombre_categoria, meta_kg "
                    "FROM categorias_viveres WHERE activo = 1 "
                    "ORDER BY id_categoria"
                )
                filas = cur.fetchall()
            finally:
                cur.close()

        metas: list[MetaDonacionBase] = []
        for fila in filas:
            nombre = fila["nombre_categoria"]
            icono, color = _ESTILOS.get(nombre, ("bi-basket-fill", "azuloscuro"))
            metas.append(
                MetaDonacionBase(
                    id=f"meta-{fila['id_categoria']}-{_slug(nombre)}",
                    categoria=nombre,
                    icono=icono,
                    meta_kg=float(fila["meta_kg"]),
                    color=color,
                )
            )
        return metas

    def recolectado_por_categoria(self) -> dict[str, float]:
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT c.nombre_categoria, "
                    "COALESCE(SUM(det.peso_estimado_kg), 0) AS total "
                    "FROM categorias_viveres c "
                    "LEFT JOIN detalle_donaciones det "
                    "ON det.id_categoria = c.id_categoria "
                    "GROUP BY c.id_categoria, c.nombre_categoria"
                )
                filas = cur.fetchall()
            finally:
                cur.close()

        return {
            fila["nombre_categoria"]: float(fila["total"] or 0)
            for fila in filas
        }
