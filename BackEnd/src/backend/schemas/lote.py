from datetime import datetime

from pydantic import Field

from .base import SchemaBase
from .catalogos import EstadoLote, UnidadMedida
from .donativo import ArticuloDonacion


class LoteCrear(SchemaBase):
    fecha_ingreso: datetime | None = None
    categoria_principal: str
    descripcion: str
    unidad: UnidadMedida = UnidadMedida.KG
    destino: str
    estado: EstadoLote = EstadoLote.PENDIENTE
    familias_beneficiadas: int = Field(default=0, ge=0)
    articulos: list[ArticuloDonacion] = Field(min_length=1)


class Lote(SchemaBase):
    id: str
    codigo: str
    fecha_ingreso: datetime
    categoria_principal: str
    descripcion: str
    volumen: float = Field(ge=0)
    unidad: UnidadMedida
    destino: str
    estado: EstadoLote
    familias_beneficiadas: int = Field(ge=0)
    articulos: list[ArticuloDonacion]


class LoteEstadoActualizar(SchemaBase):
    estado: EstadoLote


class AlertaVencimiento(SchemaBase):
    articulo_id: str
    lote_id: str
    nombre: str
    lote: str
    fecha_vencimiento: datetime
    dias_restantes: int


class KpisInventario(SchemaBase):
    total_acopiado: float
    lotes_activos: int
    lotes_entregados: int
    articulos_criticos: int
