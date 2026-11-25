"""Conexion MySQL sin ORM y utilidades de conversion de fechas."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime, time, timezone
from threading import Lock
from typing import Any

import mysql.connector
from mysql.connector import pooling

from .config import obtener_settings

_pool: pooling.MySQLConnectionPool | None = None
_lock = Lock()


def inicializar_pool() -> pooling.MySQLConnectionPool:
    """Crea el pool una sola vez. No se conecta al importar el modulo."""

    global _pool
    if _pool is not None:
        return _pool

    with _lock:
        if _pool is None:
            settings = obtener_settings()
            try:
                _pool = pooling.MySQLConnectionPool(
                    pool_name="gestion_donativos_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    **settings.database_config,
                )
            except mysql.connector.Error as exc:
                raise RuntimeError(
                    "No se pudo conectar a MySQL. Verifica BackEnd/.env y que "
                    "la base db_donativos_sanpiox exista."
                ) from exc

    return _pool


def cerrar_pool() -> None:
    """Libera la referencia al pool; las conexiones se cierran al devolverse."""

    global _pool
    with _lock:
        _pool = None


@contextmanager
def conexion() -> Iterator[mysql.connector.MySQLConnection]:
    """Entrega una conexion transaccional y hace commit/rollback."""

    pool = inicializar_pool()
    conn = pool.get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def cursor(dictionary: bool = True) -> Iterator[Any]:
    """Cursor de solo lectura/escritura con cierre automatico."""

    with conexion() as conn:
        cur = conn.cursor(dictionary=dictionary)
        try:
            yield cur
        finally:
            cur.close()


def a_datetime_utc(valor: date | datetime | None) -> datetime | None:
    """Normaliza DATE/DATETIME de MySQL a datetime UTC."""

    if valor is None:
        return None
    if isinstance(valor, datetime):
        if valor.tzinfo is None:
            return valor.replace(tzinfo=timezone.utc)
        return valor.astimezone(timezone.utc)
    return datetime.combine(valor, time.min, tzinfo=timezone.utc)


def a_date_mysql(valor: date | datetime | None) -> date | None:
    """Convierte un datetime de la API a DATE para MySQL."""

    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    return valor


def a_datetime_mysql(valor: datetime) -> datetime:
    """Convierte un datetime UTC a DATETIME naive para MySQL."""

    if valor.tzinfo is not None:
        valor = valor.astimezone(timezone.utc).replace(tzinfo=None)
    return valor
