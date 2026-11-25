export interface MetaDonacionBase {
  id: string;
  categoria: string;
  icono: string;
  metaKg: number;
  color: string;
}

export interface MetaDonacion extends MetaDonacionBase {
  recolectadoKg: number;
}

export interface HitoDonacion {
  id: string;
  fecha: Date;
  lote: string;
  titulo: string;
  descripcion: string;
  receptor: string;
  acta: string;
  estado: 'recepcionado' | 'preparacion';
}

export interface EstadisticasPublicas {
  totalKg: number;
  totalLotes: number;
  totalFamilias: number;
}
