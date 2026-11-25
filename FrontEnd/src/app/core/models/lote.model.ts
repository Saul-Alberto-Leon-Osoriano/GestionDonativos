import { ArticuloDonacion, UnidadMedida } from './donativo.model';

export type EstadoLote = 'entregado' | 'preparacion' | 'pendiente';

export interface Lote {
  id: string;
  codigo: string;
  fechaIngreso: Date;
  categoriaPrincipal: string;
  descripcion: string;
  volumen: number;
  unidad: UnidadMedida;
  destino: string;
  estado: EstadoLote;
  familiasBeneficiadas: number;
  articulos: ArticuloDonacion[];
}

export interface AlertaVencimiento {
  articuloId: string;
  loteId: string;
  nombre: string;
  lote: string;
  fechaVencimiento: Date;
  diasRestantes: number;
}

export interface KpisInventario {
  totalAcopiado: number;
  lotesActivos: number;
  lotesEntregados: number;
  articulosCriticos: number;
}

export interface RespuestaPaginada<T> {
  items: T[];
  total: number;
  pagina: number;
  tamanoPagina: number;
}
