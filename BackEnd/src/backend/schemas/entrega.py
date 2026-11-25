from datetime import date

from pydantic import Field

from .base import SchemaBase
from .catalogos import EstadoEntrega


class EntregaCrear(SchemaBase):
    id_donacion: int = Field(gt=0)
    codigo_publico_lote: str = Field(min_length=1)
    titulo_entrega: str = Field(min_length=1)
    descripcion_entrega: str = Field(min_length=1)
    coordinador_recepcion: str = Field(min_length=1)
    codigo_acta: str = Field(min_length=1)
    estado_entrega: EstadoEntrega = EstadoEntrega.PENDIENTE
    fecha_entrega: date


class Entrega(SchemaBase):
    id: int
    id_donacion: int
    codigo_publico_lote: str
    titulo_entrega: str
    descripcion_entrega: str
    coordinador_recepcion: str
    codigo_acta: str
    estado_entrega: EstadoEntrega
    fecha_entrega: date
