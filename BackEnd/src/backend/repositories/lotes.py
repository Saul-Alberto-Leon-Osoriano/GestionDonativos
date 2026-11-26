"""Repositorio de lotes/donaciones sobre MySQL."""

from datetime import datetime, timezone

from backend.database import (
    a_date_mysql,
    a_datetime_mysql,
    a_datetime_utc,
    conexion,
)
from backend.schemas import (
    ArticuloDonacion,
    DonativoDraft,
    EstadoLote,
    Lote,
    LoteCrear,
    UnidadMedida,
)

_ESTADO_BD_A_API = {
    "Nuevo": EstadoLote.PENDIENTE,
    "En Almacén": EstadoLote.PREPARACION,
    "Entregado": EstadoLote.ENTREGADO,
}
_ESTADO_API_A_BD = {estado: bd for bd, estado in _ESTADO_BD_A_API.items()}
_TIPO_DONANTE_BD = {
    "familia": "Familia / Alumno",
    "empresa": "Empresa / Aliado",
    "anonimo": "Anónimo",
}

_SELECT_DONACION = """
    SELECT
        d.id_donacion,
        d.codigo_lote,
        d.fecha_ingreso,
        d.categoria_principal,
        d.destino_solidario,
        d.observaciones_empaque,
        d.estado_lote,
        d.familias_beneficiadas,
        (
            SELECT COALESCE(SUM(det.peso_estimado_kg), 0)
            FROM detalle_donaciones det
            WHERE det.id_donacion = d.id_donacion
        ) AS volumen
    FROM donaciones d
"""


def _unidad_api(valor: str) -> UnidadMedida:
    try:
        return UnidadMedida(valor)
    except ValueError:
        return UnidadMedida.UNIDAD


def _a_articulo(fila: dict) -> ArticuloDonacion:
    cantidad = float(fila["cantidad"] or 0)
    peso_total = float(fila["peso_estimado_kg"] or 0)
    peso_unitario = round(peso_total / cantidad, 4) if cantidad else 0.0
    return ArticuloDonacion(
        id=str(fila["id_detalle"]),
        categoria=fila["nombre_categoria"],
        descripcion=fila["descripcion_producto"],
        cantidad=cantidad,
        unidad=_unidad_api(fila["unidad_medida"]),
        peso_unitario_kg=peso_unitario,
        fecha_vencimiento=a_datetime_utc(fila["fecha_vencimiento"]),
    )


def _a_lote(fila: dict, articulos: list[ArticuloDonacion]) -> Lote:
    categoria = (
        fila.get("categoria_principal")
        or (articulos[0].categoria if articulos else "Otros")
    )
    descripcion = fila.get("observaciones_empaque") or " | ".join(
        articulo.descripcion for articulo in articulos
    )
    return Lote(
        id=str(fila["id_donacion"]),
        codigo=fila["codigo_lote"],
        fecha_ingreso=a_datetime_utc(fila["fecha_ingreso"]) or datetime.now(
            timezone.utc
        ),
        categoria_principal=categoria,
        descripcion=descripcion or "Lote de donativos",
        volumen=float(fila.get("volumen") or 0),
        unidad=UnidadMedida.KG,
        destino=fila["destino_solidario"],
        estado=_ESTADO_BD_A_API.get(fila["estado_lote"], EstadoLote.PENDIENTE),
        familias_beneficiadas=int(fila.get("familias_beneficiadas") or 0),
        articulos=articulos,
    )


def _where(
    termino: str | None,
    estado: EstadoLote | None,
    categoria: str | None,
) -> tuple[str, list[object]]:
    condiciones: list[str] = []
    parametros: list[object] = []

    if termino and termino.strip():
        texto = f"%{termino.strip()}%"
        condiciones.append(
            "(d.codigo_lote LIKE %s OR d.destino_solidario LIKE %s "
            "OR d.observaciones_empaque LIKE %s OR d.categoria_principal LIKE %s)"
        )
        parametros.extend([texto, texto, texto, texto])

    if estado is not None:
        condiciones.append("d.estado_lote = %s")
        parametros.append(_ESTADO_API_A_BD[estado])

    if categoria and categoria.strip():
        condiciones.append("d.categoria_principal LIKE %s")
        parametros.append(f"%{categoria.strip()}%")

    if not condiciones:
        return "", parametros
    return " WHERE " + " AND ".join(condiciones), parametros


def _condicion_id(id_: str) -> tuple[str, object]:
    if id_.isdigit():
        return "d.id_donacion = %s", int(id_)
    return "d.codigo_lote = %s", id_


class RepositorioLotes:
    """Consultas y escrituras de donaciones y su detalle."""

    def _cargar_articulos(
        self, conn, ids: list[int]
    ) -> dict[int, list[ArticuloDonacion]]:
        if not ids:
            return {}

        marcadores = ", ".join(["%s"] * len(ids))
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT det.id_detalle, det.id_donacion, det.descripcion_producto, "
                "det.cantidad, det.unidad_medida, det.peso_estimado_kg, "
                "det.fecha_vencimiento, c.nombre_categoria "
                "FROM detalle_donaciones det "
                "JOIN categorias_viveres c ON c.id_categoria = det.id_categoria "
                f"WHERE det.id_donacion IN ({marcadores}) "
                "ORDER BY det.id_detalle",
                tuple(ids),
            )
            agrupados: dict[int, list[ArticuloDonacion]] = {id_: [] for id_ in ids}
            for fila in cur.fetchall():
                agrupados[int(fila["id_donacion"])].append(_a_articulo(fila))
            return agrupados
        finally:
            cur.close()

    def listar(
        self,
        termino: str | None = None,
        estado: EstadoLote | None = None,
        categoria: str | None = None,
    ) -> list[Lote]:
        where, parametros = _where(termino, estado, categoria)
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    _SELECT_DONACION
                    + where
                    + " ORDER BY d.fecha_ingreso DESC, d.id_donacion DESC",
                    tuple(parametros),
                )
                filas = cur.fetchall()
            finally:
                cur.close()

            ids = [int(fila["id_donacion"]) for fila in filas]
            articulos = self._cargar_articulos(conn, ids)
            return [
                _a_lote(fila, articulos.get(int(fila["id_donacion"]), []))
                for fila in filas
            ]

    def listar_paginado(
        self,
        termino: str | None,
        estado: EstadoLote | None,
        categoria: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> tuple[list[Lote], int]:
        where, parametros = _where(termino, estado, categoria)
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM donaciones d" + where,
                    tuple(parametros),
                )
                total = int(cur.fetchone()["total"])

                cur.execute(
                    _SELECT_DONACION
                    + where
                    + " ORDER BY d.fecha_ingreso DESC, d.id_donacion DESC "
                    "LIMIT %s OFFSET %s",
                    tuple(parametros)
                    + (tamano_pagina, (pagina - 1) * tamano_pagina),
                )
                filas = cur.fetchall()
            finally:
                cur.close()

            ids = [int(fila["id_donacion"]) for fila in filas]
            articulos = self._cargar_articulos(conn, ids)
            items = [
                _a_lote(fila, articulos.get(int(fila["id_donacion"]), []))
                for fila in filas
            ]
            return items, total

    def obtener_por_id(self, id_: str) -> Lote | None:
        condicion, valor = _condicion_id(id_)
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    _SELECT_DONACION + f" WHERE {condicion} LIMIT 1",
                    (valor,),
                )
                fila = cur.fetchone()
            finally:
                cur.close()

            if not fila:
                return None

            articulos = self._cargar_articulos(conn, [int(fila["id_donacion"])])
            return _a_lote(fila, articulos.get(int(fila["id_donacion"]), []))

    def _siguiente_codigo_lote(self, cur, fecha: datetime) -> str:
        prefijo = f"#PX-LOT-{fecha.year}-"
        cur.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(codigo_lote, '-', -1) "
            "AS UNSIGNED)), 0) AS maximo FROM donaciones "
            "WHERE codigo_lote LIKE %s",
            (f"{prefijo}%",),
        )
        maximo = int(cur.fetchone()["maximo"])
        return f"{prefijo}{maximo + 1:03d}"

    def _obtener_o_crear_categoria(self, cur, nombre: str) -> int:
        nombre = (nombre or "").strip() or "Otros"
        cur.execute(
            "SELECT id_categoria FROM categorias_viveres "
            "WHERE nombre_categoria = %s LIMIT 1",
            (nombre,),
        )
        fila = cur.fetchone()
        if fila:
            return int(fila["id_categoria"])

        cur.execute(
            "INSERT INTO categorias_viveres (nombre_categoria, meta_kg) "
            "VALUES (%s, %s)",
            (nombre, 500.00),
        )
        return int(cur.lastrowid)

    def _obtener_o_crear_donante_anonimo(self, cur) -> int:
        cur.execute(
            "SELECT id_donante FROM donantes "
            "WHERE tipo_donante = %s LIMIT 1",
            ("Anónimo",),
        )
        fila = cur.fetchone()
        if fila:
            return int(fila["id_donante"])

        cur.execute(
            "INSERT INTO donantes "
            "(id_usuario, tipo_donante, nombre_razon_social, dni_ruc, "
            "grado_seccion, telefono_whatsapp) "
            "VALUES (NULL, %s, %s, NULL, NULL, NULL)",
            ("Anónimo", "Donante anónimo"),
        )
        return int(cur.lastrowid)

    def _insertar_detalles(self, cur, id_donacion: int, articulos: list) -> None:
        for articulo in articulos:
            if articulo.fecha_vencimiento is None:
                raise ValueError(
                    "La fecha de vencimiento es obligatoria para cada articulo."
                )
            id_categoria = self._obtener_o_crear_categoria(cur, articulo.categoria)
            peso_total = round(
                float(articulo.cantidad) * float(articulo.peso_unitario_kg or 0),
                2,
            )
            cur.execute(
                "INSERT INTO detalle_donaciones "
                "(id_donacion, id_categoria, descripcion_producto, cantidad, "
                "unidad_medida, peso_estimado_kg, fecha_vencimiento) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    id_donacion,
                    id_categoria,
                    articulo.descripcion.strip(),
                    articulo.cantidad,
                    articulo.unidad.value,
                    peso_total,
                    a_date_mysql(articulo.fecha_vencimiento),
                ),
            )

    def _insertar_donacion(
        self,
        cur,
        *,
        codigo: str,
        id_donante: int,
        id_agente_pastoral: int,
        datos: LoteCrear,
        fecha: datetime,
    ) -> int:
        cur.execute(
            "INSERT INTO donaciones "
            "(codigo_lote, id_donante, id_agente_pastoral, destino_solidario, "
            "observaciones_empaque, estado_lote, fecha_ingreso, "
            "categoria_principal, familias_beneficiadas) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                codigo,
                id_donante,
                id_agente_pastoral,
                datos.destino.strip(),
                datos.descripcion.strip(),
                _ESTADO_API_A_BD[datos.estado],
                a_datetime_mysql(fecha),
                datos.categoria_principal.strip() or "Otros",
                datos.familias_beneficiadas,
            ),
        )
        return int(cur.lastrowid)

    def crear(self, datos: LoteCrear, id_agente_pastoral: int) -> Lote:
        fecha = datos.fecha_ingreso or datetime.now(timezone.utc)
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        else:
            fecha = fecha.astimezone(timezone.utc)

        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                id_donante = self._obtener_o_crear_donante_anonimo(cur)
                codigo = self._siguiente_codigo_lote(cur, fecha)
                id_donacion = self._insertar_donacion(
                    cur,
                    codigo=codigo,
                    id_donante=id_donante,
                    id_agente_pastoral=id_agente_pastoral,
                    datos=datos,
                    fecha=fecha,
                )
                self._insertar_detalles(cur, id_donacion, datos.articulos)
            finally:
                cur.close()

        lote = self.obtener_por_id(str(id_donacion))
        if lote is None:
            raise RuntimeError("El lote se inserto pero no se pudo leer.")
        return lote

    def crear_desde_donativo(
        self,
        draft: DonativoDraft,
        datos: LoteCrear,
        id_agente_pastoral: int,
    ) -> Lote:
        fecha = datos.fecha_ingreso or datetime.now(timezone.utc)
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        else:
            fecha = fecha.astimezone(timezone.utc)

        tipo_bd = _TIPO_DONANTE_BD.get(draft.donante.tipo.value, "Anónimo")
        nombre = draft.donante.nombre.strip() or "Donante anónimo"

        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "INSERT INTO donantes "
                    "(id_usuario, tipo_donante, nombre_razon_social, dni_ruc, "
                    "grado_seccion, telefono_whatsapp) "
                    "VALUES (NULL, %s, %s, %s, %s, %s)",
                    (
                        tipo_bd,
                        nombre,
                        draft.donante.documento.strip() or None,
                        draft.donante.grado_seccion.strip() or None,
                        draft.donante.telefono.strip() or None,
                    ),
                )
                id_donante = int(cur.lastrowid)
                codigo = self._siguiente_codigo_lote(cur, fecha)
                id_donacion = self._insertar_donacion(
                    cur,
                    codigo=codigo,
                    id_donante=id_donante,
                    id_agente_pastoral=id_agente_pastoral,
                    datos=datos,
                    fecha=fecha,
                )
                self._insertar_detalles(cur, id_donacion, datos.articulos)
            finally:
                cur.close()

        lote = self.obtener_por_id(str(id_donacion))
        if lote is None:
            raise RuntimeError("El lote se inserto pero no se pudo leer.")
        return lote

    def actualizar_estado(self, id_: str, estado: EstadoLote) -> Lote | None:
        condicion, valor = _condicion_id(id_)
        condicion = condicion.replace("d.", "")
        with conexion() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    f"UPDATE donaciones SET estado_lote = %s WHERE {condicion}",
                    (_ESTADO_API_A_BD[estado], valor),
                )
            finally:
                cur.close()
        return self.obtener_por_id(id_)

    def eliminar(self, id_: str) -> bool:
        condicion, valor = _condicion_id(id_)
        condicion = condicion.replace("d.", "")
        with conexion() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    f"DELETE FROM donaciones WHERE {condicion}",
                    (valor,),
                )
                return cur.rowcount > 0
            finally:
                cur.close()
