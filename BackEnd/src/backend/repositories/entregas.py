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
