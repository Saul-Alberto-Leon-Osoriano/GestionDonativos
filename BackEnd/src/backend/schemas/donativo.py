from datetime import datetime

from pydantic import Field

from .base import SchemaBase
from .catalogos import TipoDonante, UnidadMedida


class DatosDonante(SchemaBase):
    tipo: TipoDonante
    nombre: str = ""
    documento: str = ""
    grado_seccion: str = ""
    telefono: str = ""


class ArticuloDonacion(SchemaBase):
    id: str
    categoria: str
    descripcion: str
    cantidad: float = Field(gt=0)
    unidad: UnidadMedida
    peso_unitario_kg: float | None = Field(default=None, ge=0)
    fecha_vencimiento: datetime | None = None


class DonativoDraft(SchemaBase):
    donante: DatosDonante
    articulos: list[ArticuloDonacion] = Field(min_length=1)
    observaciones: str = ""
    destino: str = ""


class ResumenDonativo(SchemaBase):
    total_articulos: int
    total_unidades: float
    peso_neto_kg: float
    articulos_por_vencer: int
