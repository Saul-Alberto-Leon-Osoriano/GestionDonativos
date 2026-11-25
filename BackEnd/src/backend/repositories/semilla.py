"""Datos semilla en memoria, espejo de FrontEnd/src/app/core/data/mock-data.ts."""

from datetime import datetime, timezone

from backend.schemas import (
    ArticuloDonacion,
    EstadoLote,
    Lote,
    MetaDonacionBase,
    UnidadMedida,
    Usuario,
)


def _fecha(anio: int, mes: int, dia: int, hora: int = 0, minuto: int = 0) -> datetime:
    """Construye fecha UTC con `mes` en base 0, igual que fechaUTC() en Angular."""
    return datetime(anio, mes + 1, dia, hora, minuto, tzinfo=timezone.utc)


def _articulo(
    id_: str,
    categoria: str,
    descripcion: str,
    cantidad: float,
    unidad: UnidadMedida,
    peso_unitario_kg: float,
    fecha_vencimiento: datetime,
) -> ArticuloDonacion:
    return ArticuloDonacion(
        id=id_,
        categoria=categoria,
        descripcion=descripcion,
        cantidad=cantidad,
        unidad=unidad,
        peso_unitario_kg=peso_unitario_kg,
        fecha_vencimiento=fecha_vencimiento,
    )


def _lote(
    id_: str,
    codigo: str,
    fecha_ingreso: datetime,
    categoria_principal: str,
    descripcion: str,
    destino: str,
    estado: EstadoLote,
    familias_beneficiadas: int,
    articulos: list[ArticuloDonacion],
) -> Lote:
    volumen = round(
        sum(
            articulo.cantidad * (articulo.peso_unitario_kg or 0)
            for articulo in articulos
        ),
        2,
    )
    return Lote(
        id=id_,
        codigo=codigo,
        fecha_ingreso=fecha_ingreso,
        categoria_principal=categoria_principal,
        descripcion=descripcion,
        volumen=volumen,
        unidad=UnidadMedida.KG,
        destino=destino,
        estado=estado,
        familias_beneficiadas=familias_beneficiadas,
        articulos=articulos,
    )


_LOTES_SEMILLA: tuple[Lote, ...] = (
    _lote(
        "lote-041",
        "#PX-LOT-2026-041",
        _fecha(2026, 10, 18),
        "Arroz, Avena y Menestras",
        "Arroz superior y lentejas serranas",
        "Cáritas Huancayo",
        EstadoLote.ENTREGADO,
        45,
        [
            _articulo(
                "a-041-1",
                "Arroz, Avena y Menestras",
                "Arroz superior (saco 50 kg)",
                60,
                UnidadMedida.KG,
                1,
                _fecha(2027, 5, 15),
            ),
            _articulo(
                "a-041-2",
                "Arroz, Avena y Menestras",
                "Lenteja serrana (bolsa 1 kg)",
                40,
                UnidadMedida.KG,
                1,
                _fecha(2027, 3, 20),
            ),
        ],
    ),
    _lote(
        "lote-042",
        "#PX-LOT-2026-042",
        _fecha(2026, 10, 20),
        "Leche evaporada y Suplementos de bebé",
        "Leche evaporada y fórmula infantil",
        'Comedor Popular "Santa Rosa"',
        EstadoLote.PREPARACION,
        30,
        [
            _articulo(
                "a-042-1",
                "Leche evaporada y Suplementos de bebé",
                "Leche evaporada entera (lata 400 g)",
                48,
                UnidadMedida.UNIDAD,
                0.4,
                _fecha(2027, 1, 10),
            ),
            _articulo(
                "a-042-2",
                "Leche evaporada y Suplementos de bebé",
                "Fórmula infantil etapa 2 (bolsa 800 g)",
                12,
                UnidadMedida.PAQUETE,
                0.8,
                _fecha(2026, 11, 28),
            ),
        ],
    ),
    _lote(
        "lote-043",
        "#PX-LOT-2026-043",
        _fecha(2026, 10, 22),
        "Galletas y Cereales",
        "Galletas fortificadas y avena",
        "Hogar de Niños San José",
        EstadoLote.PENDIENTE,
        20,
        [
            _articulo(
                "a-043-1",
                "Galletas y Cereales",
                "Galletas fortificadas de quinua (paquete)",
                30,
                UnidadMedida.PAQUETE,
                0.5,
                _fecha(2026, 11, 5),
            ),
            _articulo(
                "a-043-2",
                "Galletas y Cereales",
                "Avena instantánea (bolsa 1 kg)",
                10,
                UnidadMedida.KG,
                1,
                _fecha(2027, 0, 15),
            ),
        ],
    ),
    _lote(
        "lote-044",
        "#PX-LOT-2026-044",
        _fecha(2026, 10, 23),
        "Conservas de Pescado & Aceites",
        "Atún en aceite y aceite vegetal",
        "Cáritas Huancayo",
        EstadoLote.ENTREGADO,
        60,
        [
            _articulo(
                "a-044-1",
                "Conservas de Pescado & Aceites",
                "Atún en aceite (lata 170 g)",
                72,
                UnidadMedida.UNIDAD,
                0.17,
                _fecha(2028, 2, 12),
            ),
            _articulo(
                "a-044-2",
                "Conservas de Pescado & Aceites",
                "Aceite vegetal (botella 1 L)",
                24,
                UnidadMedida.UNIDAD,
                0.9,
                _fecha(2027, 7, 8),
            ),
        ],
    ),
    _lote(
        "lote-045",
        "#PX-LOT-2026-045",
        _fecha(2026, 10, 24),
        "Fideos y Sémolas Diversas",
        "Fideos y sémola de trigo",
        "Comedor San José",
        EstadoLote.PREPARACION,
        18,
        [
            _articulo(
                "a-045-1",
                "Fideos y Sémolas Diversas",
                "Fideos tallarín (bolsa 500 g)",
                50,
                UnidadMedida.KG,
                1,
                _fecha(2027, 4, 30),
            ),
            _articulo(
                "a-045-2",
                "Fideos y Sémolas Diversas",
                "Sémola de trigo (bolsa 1 kg)",
                15,
                UnidadMedida.KG,
                1,
                _fecha(2026, 11, 10),
            ),
        ],
    ),
)

_USUARIOS_SEMILLA: tuple[Usuario, ...] = (
    Usuario(
        id="A001",
        nombre="Prof. Taipe",
        telefono="+51 999 999 999",
        correo="pastoral@sanpiox.edu.pe",
        rol="administrativo",
        activo=True,
    ),
    Usuario(
        id="A002",
        nombre="Hna. Teresa Gómez",
        telefono="+51 988 777 666",
        correo="teresa.gomez@sanpiox.edu.pe",
        rol="administrativo",
        activo=True,
    ),
    Usuario(
        id="U001",
        nombre="Familia Quispe",
        telefono="+51 964 123 456",
        correo="donante@sanpiox.edu.pe",
        rol="donante",
        activo=True,
    ),
    Usuario(
        id="U002",
        nombre="Familia Huamán",
        telefono="+51 955 321 789",
        correo="familia.huaman@correo.com",
        rol="donante",
        activo=True,
    ),
    Usuario(
        id="U003",
        nombre="Empresa Andina S.A.C.",
        telefono="+51 944 555 222",
        correo="donaciones@empresaandina.pe",
        rol="donante",
        activo=False,
    ),
)

_METAS_BASE_SEMILLA: tuple[MetaDonacionBase, ...] = (
    MetaDonacionBase(
        id="meta-arroz",
        categoria="Arroz, Avena y Menestras",
        icono="bi-flower1",
        meta_kg=500,
        color="naranjaoscuro",
    ),
    MetaDonacionBase(
        id="meta-conservas",
        categoria="Conservas de Pescado & Aceites",
        icono="bi-tsunami",
        meta_kg=500,
        color="azuloscuro",
    ),
    MetaDonacionBase(
        id="meta-leche",
        categoria="Leche evaporada y Suplementos de bebé",
        icono="bi-person-arms-up",
        meta_kg=500,
        color="verdeoscuro",
    ),
    MetaDonacionBase(
        id="meta-fideos",
        categoria="Fideos y Sémolas Diversas",
        icono="bi-cup-hot-fill",
        meta_kg=500,
        color="moradooscuro",
    ),
)
