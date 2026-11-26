"""Repositorio de actas y entregas publicadas en Transparencia."""

from backend.database import a_datetime_utc, conexion
from backend.schemas import (
    Entrega,
    EntregaCrear,
    EstadoEntrega,
    EstadoHito,
    HitoDonacion,
)

_SELECT_ENTREGA = """
    SELECT
        e.id_entrega,
        e.id_donacion,
        e.codigo_publico_lote,
        e.titulo_entrega,
        e.descripcion_entrega,
        e.coordinador_recepcion,
        e.codigo_acta,
        e.estado_entrega,
        e.fecha_entrega,
        d.codigo_lote
    FROM entregas_transparencia e
    JOIN donaciones d ON d.id_donacion = e.id_donacion
"""


def _a_entrega(fila: dict) -> Entrega:
    return Entrega(
        id=int(fila["id_entrega"]),
        id_donacion=int(fila["id_donacion"]),
        codigo_publico_lote=fila["codigo_publico_lote"],
        titulo_entrega=fila["titulo_entrega"],
        descripcion_entrega=fila["descripcion_entrega"],
        coordinador_recepcion=fila["coordinador_recepcion"],
        codigo_acta=fila["codigo_acta"],
        estado_entrega=EstadoEntrega(fila["estado_entrega"]),
        fecha_entrega=fila["fecha_entrega"],
    )


class RepositorioEntregas:
    """Lectura de hitos y registro de actas."""

    def obtener_por_donacion(self, id_donacion: int) -> Entrega | None:
        """Devuelve el acta mas reciente del lote, si ya fue publicada."""

        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    _SELECT_ENTREGA
                    + " WHERE e.id_donacion = %s "
                    "ORDER BY e.id_entrega DESC LIMIT 1",
                    (id_donacion,),
                )
                fila = cur.fetchone()
            finally:
                cur.close()

        return _a_entrega(fila) if fila else None

    def siguiente_codigo_acta(self) -> str:
        """Genera un codigo de acta consecutivo con el formato #ACTA-XXXX."""

        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(codigo_acta, "
                    "'-', -1) AS UNSIGNED)), 0) AS maximo "
                    "FROM entregas_transparencia "
                    "WHERE codigo_acta LIKE %s",
                    ("#ACTA-%",),
                )
                fila = cur.fetchone()
            finally:
                cur.close()

        maximo = int(fila["maximo"]) if fila else 0
        return f"#ACTA-{maximo + 1:04d}"

    def marcar_entregada_por_donacion(self, id_donacion: int) -> None:
        """Publica como entregada un acta previa del lote (evita duplicados)."""

        with conexion() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE entregas_transparencia SET estado_entrega = %s "
                    "WHERE id_donacion = %s",
                    (EstadoEntrega.ENTREGADO.value, id_donacion),
                )
            finally:
                cur.close()

    def eliminar_por_donacion(self, id_donacion: int) -> int:
        """Retira las actas del lote cuando deja de estar entregado."""

        with conexion() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "DELETE FROM entregas_transparencia "
                    "WHERE id_donacion = %s",
                    (id_donacion,),
                )
                return int(cur.rowcount)
            finally:
                cur.close()

    def listar_hitos(self) -> list[HitoDonacion]:
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    _SELECT_ENTREGA
                    + " ORDER BY e.fecha_entrega DESC, e.id_entrega DESC"
                )
                filas = cur.fetchall()
            finally:
                cur.close()

        hitos: list[HitoDonacion] = []
        for fila in filas:
            entregado = fila["estado_entrega"] == EstadoEntrega.ENTREGADO.value
            hitos.append(
                HitoDonacion(
                    id=f"entrega-{fila['id_entrega']}",
                    fecha=a_datetime_utc(fila["fecha_entrega"]),
                    lote=fila["codigo_lote"],
                    titulo=fila["titulo_entrega"],
                    descripcion=fila["descripcion_entrega"],
                    receptor=fila["coordinador_recepcion"],
                    acta=fila["codigo_acta"],
                    estado=(
                        EstadoHito.RECEPCIONADO
                        if entregado
                        else EstadoHito.PREPARACION
                    ),
                )
            )
        return hitos

    def crear(self, datos: EntregaCrear, id_agente_registra: int) -> Entrega:
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "INSERT INTO entregas_transparencia "
                    "(id_donacion, id_agente_registra, codigo_publico_lote, "
                    "titulo_entrega, descripcion_entrega, coordinador_recepcion, "
                    "codigo_acta, estado_entrega, fecha_entrega) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        datos.id_donacion,
                        id_agente_registra,
                        datos.codigo_publico_lote.strip(),
                        datos.titulo_entrega.strip(),
                        datos.descripcion_entrega.strip(),
                        datos.coordinador_recepcion.strip(),
                        datos.codigo_acta.strip(),
                        datos.estado_entrega.value,
                        datos.fecha_entrega,
                    ),
                )
                id_entrega = int(cur.lastrowid)
                cur.execute(
                    _SELECT_ENTREGA + " WHERE e.id_entrega = %s",
                    (id_entrega,),
                )
                fila = cur.fetchone()
            finally:
                cur.close()

        if not fila:
            raise RuntimeError("La entrega se inserto pero no se pudo leer.")
        return _a_entrega(fila)
