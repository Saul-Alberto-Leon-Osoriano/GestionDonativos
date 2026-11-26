"""Repositorio de usuarios sobre MySQL, con SQL parametrizado."""

from dataclasses import dataclass

from mysql.connector import IntegrityError

from backend.database import conexion
from backend.schemas import RolUsuario, Usuario, UsuarioCrear

_COLUMNAS = """
    id_usuario,
    codigo_usuario,
    nombre_completo,
    correo_electronico,
    password_hash,
    telefono,
    tipo_usuario,
    estado
"""


@dataclass(frozen=True)
class CredencialesUsuario:
    id_usuario: int
    codigo_usuario: str
    nombre_completo: str
    correo_electronico: str
    password_hash: str
    telefono: str | None
    tipo_usuario: str
    estado: int

    @property
    def activo(self) -> bool:
        return bool(self.estado)

    @property
    def rol(self) -> RolUsuario:
        return RolUsuario(self.tipo_usuario.lower())


def _a_usuario(fila: dict) -> Usuario:
    return Usuario(
        id=fila["codigo_usuario"],
        id_usuario=fila["id_usuario"],
        nombre=fila["nombre_completo"],
        telefono=fila["telefono"] or "",
        correo=fila["correo_electronico"],
        rol=RolUsuario(fila["tipo_usuario"].lower()),
        activo=bool(fila["estado"]),
    )


def _a_credenciales(fila: dict) -> CredencialesUsuario:
    return CredencialesUsuario(
        id_usuario=fila["id_usuario"],
        codigo_usuario=fila["codigo_usuario"],
        nombre_completo=fila["nombre_completo"],
        correo_electronico=fila["correo_electronico"],
        password_hash=fila["password_hash"],
        telefono=fila["telefono"],
        tipo_usuario=fila["tipo_usuario"],
        estado=fila["estado"],
    )


class RepositorioUsuarios:
    """CRUD de usuarios y consulta de credenciales."""

    def listar(self) -> list[Usuario]:
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    f"SELECT {_COLUMNAS} FROM usuarios ORDER BY codigo_usuario"
                )
                return [_a_usuario(fila) for fila in cur.fetchall()]
            finally:
                cur.close()

    def obtener_por_id(self, id_: str) -> Usuario | None:
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    f"SELECT {_COLUMNAS} FROM usuarios WHERE codigo_usuario = %s",
                    (id_,),
                )
                fila = cur.fetchone()
                return _a_usuario(fila) if fila else None
            finally:
                cur.close()

    def obtener_por_correo(self, correo: str) -> Usuario | None:
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    f"SELECT {_COLUMNAS} FROM usuarios "
                    "WHERE correo_electronico = %s",
                    (correo.strip(),),
                )
                fila = cur.fetchone()
                return _a_usuario(fila) if fila else None
            finally:
                cur.close()

    def obtener_credenciales(self, correo: str) -> CredencialesUsuario | None:
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    f"SELECT {_COLUMNAS} FROM usuarios "
                    "WHERE correo_electronico = %s",
                    (correo.strip(),),
                )
                fila = cur.fetchone()
                return _a_credenciales(fila) if fila else None
            finally:
                cur.close()

    def existe_correo(self, correo: str, excluir_id: str | None = None) -> bool:
        sql = "SELECT 1 FROM usuarios WHERE correo_electronico = %s"
        parametros: list[object] = [correo.strip()]
        if excluir_id:
            sql += " AND codigo_usuario <> %s"
            parametros.append(excluir_id)

        with conexion() as conn:
            cur = conn.cursor()
            try:
                cur.execute(sql + " LIMIT 1", tuple(parametros))
                return cur.fetchone() is not None
            finally:
                cur.close()

    def siguiente_codigo(self, rol: RolUsuario) -> str:
        prefijo = "A" if rol == RolUsuario.ADMINISTRATIVO else "U"
        with conexion() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT COALESCE(MAX(CAST(SUBSTRING(codigo_usuario, 2) "
                    "AS UNSIGNED)), 0) AS maximo FROM usuarios "
                    "WHERE codigo_usuario LIKE %s",
                    (f"{prefijo}%",),
                )
                maximo = int(cur.fetchone()["maximo"])
            finally:
                cur.close()

        return f"{prefijo}{maximo + 1:03d}"

    def crear(
        self,
        datos: UsuarioCrear,
        password_hash: str,
        creado_por_id: int | None = None,
    ) -> Usuario:
        tipo_usuario = (
            "Administrativo"
            if datos.rol == RolUsuario.ADMINISTRATIVO
            else "Donante"
        )

        ultimo_error: IntegrityError | None = None
        for _ in range(3):
            codigo = self.siguiente_codigo(datos.rol)
            try:
                with conexion() as conn:
                    cur = conn.cursor()
                    try:
                        cur.execute(
                            "INSERT INTO usuarios "
                            "(codigo_usuario, nombre_completo, correo_electronico, "
                            "password_hash, telefono, tipo_usuario, creado_por_id, "
                            "estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                            (
                                codigo,
                                datos.nombre.strip(),
                                datos.correo.strip(),
                                password_hash,
                                datos.telefono.strip(),
                                tipo_usuario,
                                creado_por_id,
                                1 if datos.activo else 0,
                            ),
                        )
                    finally:
                        cur.close()
                usuario = self.obtener_por_id(codigo)
                if usuario is None:
                    raise RuntimeError("El usuario se inserto pero no se pudo leer.")
                return usuario
            except IntegrityError as exc:
                ultimo_error = exc
                if "codigo_usuario" not in str(exc):
                    raise

        raise ultimo_error or RuntimeError("No se pudo generar un codigo unico.")

    def actualizar(self, id_: str, cambios: dict[str, object]) -> Usuario | None:
        if not cambios:
            return self.obtener_por_id(id_)

        mapa_columnas = {
            "codigo_usuario": "codigo_usuario",
            "nombre": "nombre_completo",
            "correo": "correo_electronico",
            "telefono": "telefono",
            "password_hash": "password_hash",
            "rol": "tipo_usuario",
            "activo": "estado",
        }

        asignaciones: list[str] = []
        valores: list[object] = []
        for clave, valor in cambios.items():
            columna = mapa_columnas.get(clave)
            if columna is None:
                continue
            if clave == "rol":
                valor = (
                    "Administrativo"
                    if valor == RolUsuario.ADMINISTRATIVO
                    else "Donante"
                )
            elif clave == "activo":
                valor = 1 if valor else 0
            asignaciones.append(f"{columna} = %s")
            valores.append(valor)

        if not asignaciones:
            return self.obtener_por_id(id_)

        valores.append(id_)
        with conexion() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE usuarios SET " + ", ".join(asignaciones) +
                    " WHERE codigo_usuario = %s",
                    tuple(valores),
                )
            finally:
                cur.close()

        nuevo_id = str(cambios.get("codigo_usuario") or id_)
        return self.obtener_por_id(nuevo_id)

    def eliminar(self, id_: str) -> bool:
        """Borrado logico para no romper las FKs historicas."""

        with conexion() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE usuarios SET estado = 0 WHERE codigo_usuario = %s",
                    (id_,),
                )
                return cur.rowcount > 0
            finally:
                cur.close()

    def registrar_solicitud_recuperacion(self, correo: str) -> None:
        with conexion() as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO solicitudes_recuperacion "
                    "(correo_electronico) VALUES (%s)",
                    (correo.strip(),),
                )
            finally:
                cur.close()
