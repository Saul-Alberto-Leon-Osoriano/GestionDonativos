export type TipoDonante = 'familia' | 'empresa' | 'anonimo';

export type UnidadMedida = 'Unid.' | 'Kg' | 'Paq.';

export interface DatosDonante {
  tipo: TipoDonante;
  nombre: string;
  documento: string;
  gradoSeccion: string;
  telefono: string;
}

export interface ArticuloDonacion {
  id: string;
  categoria: string;
  descripcion: string;
  cantidad: number;
  unidad: UnidadMedida;
  pesoUnitarioKg: number | null;
  fechaVencimiento: Date | null;
}

export interface DonativoDraft {
  donante: DatosDonante;
  articulos: ArticuloDonacion[];
  observaciones: string;
  destino: string;
}

export interface ResumenDonativo {
  totalArticulos: number;
  totalUnidades: number;
  pesoNetoKg: number;
  articulosPorVencer: number;
}

export const TIPOS_DONANTE: readonly {
  valor: TipoDonante;
  etiqueta: string;
  icono: string;
}[] = [
  { valor: 'familia', etiqueta: 'Familia / Alumno', icono: 'bi-mortarboard-fill' },
  { valor: 'empresa', etiqueta: 'Empresa / Aliado', icono: 'bi-building-fill' },
  { valor: 'anonimo', etiqueta: 'Anónimo', icono: 'bi-incognito' },
];

export const UNIDADES_MEDIDA: readonly UnidadMedida[] = ['Unid.', 'Kg', 'Paq.'];

export const CATEGORIAS_ALIMENTO: readonly string[] = [
  'Arroz, Avena y Menestras',
  'Conservas de Pescado & Aceites',
  'Leche evaporada y Suplementos de bebé',
  'Fideos y Sémolas Diversas',
  'Galletas y Cereales',
  'Menestras y Granos',
  'Lácteos y Harinas',
  'Otros',
];

let articuloSecuencia = 0;

export function crearArticuloVacio(): ArticuloDonacion {
  articuloSecuencia += 1;
  return {
    id: `art-${Date.now()}-${articuloSecuencia}`,
    categoria: '',
    descripcion: '',
    cantidad: 1,
    unidad: 'Unid.',
    pesoUnitarioKg: null,
    fechaVencimiento: null,
  };
}

export function crearDonativoVacio(): DonativoDraft {
  return {
    donante: {
      tipo: 'familia',
      nombre: '',
      documento: '',
      gradoSeccion: '',
      telefono: '',
    },
    articulos: [crearArticuloVacio()],
    observaciones: '',
    destino: '',
  };
}

export function calcularPesoNeto(articulos: readonly ArticuloDonacion[]): number {
  return articulos.reduce(
    (total, articulo) =>
      total + (Number(articulo.cantidad) || 0) * (Number(articulo.pesoUnitarioKg) || 0),
    0,
  );
}

/**
 * Construye una fecha "de calendario" en UTC. Los `<input type="date">` de
 * Signal Forms entregan `Date` a medianoche UTC, por lo que todo el modelo usa
 * el mismo criterio para evitar desfases por zona horaria.
 */
export function fechaUTC(
  anio: number,
  mes: number,
  dia: number,
  hora = 0,
  minuto = 0,
): Date {
  return new Date(Date.UTC(anio, mes, dia, hora, minuto));
}

export function hoyUTC(): Date {
  const hoy = new Date();
  return fechaUTC(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());
}

export function diasHasta(fecha: Date): number {
  const objetivo = fechaUTC(
    fecha.getUTCFullYear(),
    fecha.getUTCMonth(),
    fecha.getUTCDate(),
  );
  return Math.round((objetivo.getTime() - hoyUTC().getTime()) / 86_400_000);
}

export function formatearFecha(fecha: Date | null): string {
  if (!fecha) {
    return 'Sin fecha';
  }

  return new Intl.DateTimeFormat('es-PE', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(fecha);
}

export function calcularResumenDonativo(draft: DonativoDraft): ResumenDonativo {
  const totalUnidades = draft.articulos.reduce(
    (total, articulo) => total + (Number(articulo.cantidad) || 0),
    0,
  );

  return {
    totalArticulos: draft.articulos.length,
    totalUnidades,
    pesoNetoKg: calcularPesoNeto(draft.articulos),
    articulosPorVencer: draft.articulos.filter(
      (articulo) =>
        articulo.fechaVencimiento !== null &&
        diasHasta(articulo.fechaVencimiento) >= 0 &&
        diasHasta(articulo.fechaVencimiento) <= 30,
    ).length,
  };
}
