from datetime import datetime, timezone


def utc_actual() -> datetime:
    """Devuelve la fecha y hora actual en UTC."""
    return datetime.now(timezone.utc)


def normalizar_utc(fecha: datetime) -> datetime:
    """Convierte cualquier datetime a UTC; si es naive, se interpreta como UTC."""
    if fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)
    return fecha.astimezone(timezone.utc)


def fecha_calendario_utc(fecha: datetime) -> datetime:
    """Recorta un datetime a medianza UTC, igual que fechaUTC() en Angular."""
    fecha_utc = normalizar_utc(fecha)
    return datetime(fecha_utc.year, fecha_utc.month, fecha_utc.day, tzinfo=timezone.utc)


def hoy_utc() -> datetime:
    """Medianoche UTC del dia actual."""
    ahora = utc_actual()
    return datetime(ahora.year, ahora.month, ahora.day, tzinfo=timezone.utc)


def dias_hasta(fecha: datetime) -> int:
    """Dias de diferencia entre la fecha objetivo y hoy, ambos a medianoche UTC."""
    objetivo = fecha_calendario_utc(fecha)
    return round((objetivo - hoy_utc()).total_seconds() / 86_400)
