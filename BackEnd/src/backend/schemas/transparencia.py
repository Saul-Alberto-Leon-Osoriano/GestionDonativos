from datetime import datetime

from pydantic import Field

from .base import SchemaBase
from .catalogos import EstadoHito


class MetaDonacionBase(SchemaBase):
    id: str
    categoria: str
    icono: str
    meta_kg: float = Field(ge=0)
    color: str


class MetaDonacion(MetaDonacionBase):
    recolectado_kg: float = Field(ge=0)


class HitoDonacion(SchemaBase):
    id: str
    fecha: datetime
    lote: str
    titulo: str
    descripcion: str
    receptor: str
    acta: str
    estado: EstadoHito


class EstadisticasPublicas(SchemaBase):
    total_kg: float = Field(ge=0)
    total_lotes: int = Field(ge=0)
    total_familias: int = Field(ge=0)
