from enum import Enum


class TipoDonante(str, Enum):
    FAMILIA = "familia"
    EMPRESA = "empresa"
    ANONIMO = "anonimo"


class UnidadMedida(str, Enum):
    UNIDAD = "Unid."
    KG = "Kg"
    PAQUETE = "Paq."


class EstadoLote(str, Enum):
    ENTREGADO = "entregado"
    PREPARACION = "preparacion"
    PENDIENTE = "pendiente"


class RolUsuario(str, Enum):
    DONANTE = "donante"
    ADMINISTRATIVO = "administrativo"


class EstadoHito(str, Enum):
    RECEPCIONADO = "recepcionado"
    PREPARACION = "preparacion"


CATEGORIAS_ALIMENTO: tuple[str, ...] = (
    "Arroz, Avena y Menestras",
    "Conservas de Pescado & Aceites",
    "Leche evaporada y Suplementos de bebé",
    "Fideos y Sémolas Diversas",
    "Galletas y Cereales",
    "Menestras y Granos",
    "Lácteos y Harinas",
    "Otros",
)

TIPOS_DONANTE: tuple[dict[str, str], ...] = (
    {"valor": TipoDonante.FAMILIA.value, "etiqueta": "Familia / Alumno", "icono": "bi-mortarboard-fill"},
    {"valor": TipoDonante.EMPRESA.value, "etiqueta": "Empresa / Aliado", "icono": "bi-building-fill"},
    {"valor": TipoDonante.ANONIMO.value, "etiqueta": "Anónimo", "icono": "bi-incognito"},
)

UNIDADES_MEDIDA: tuple[UnidadMedida, ...] = (
    UnidadMedida.UNIDAD,
    UnidadMedida.KG,
    UnidadMedida.PAQUETE,
)
