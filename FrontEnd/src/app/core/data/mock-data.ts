import { ArticuloDonacion, calcularPesoNeto, fechaUTC, UnidadMedida } from '../models/donativo.model';
import { Lote } from '../models/lote.model';
import { MetaDonacionBase } from '../models/transparencia.model';
import { RolUsuario, Usuario } from '../models/usuario.model';
import { SolicitudRecuperacion } from '../models/auth.model';

function articulo(
  id: string,
  categoria: string,
  descripcion: string,
  cantidad: number,
  unidad: UnidadMedida,
  pesoUnitarioKg: number,
  fechaVencimiento: Date,
): ArticuloDonacion {
  return {
    id,
    categoria,
    descripcion,
    cantidad,
    unidad,
    pesoUnitarioKg,
    fechaVencimiento,
  };
}

function lote(
  id: string,
  codigo: string,
  fechaIngreso: Date,
  categoriaPrincipal: string,
  descripcion: string,
  destino: string,
  estado: Lote['estado'],
  familiasBeneficiadas: number,
  articulos: ArticuloDonacion[],
): Lote {
  return {
    id,
    codigo,
    fechaIngreso,
    categoriaPrincipal,
    descripcion,
    volumen: Math.round(calcularPesoNeto(articulos) * 100) / 100,
    unidad: 'Kg',
    destino,
    estado,
    familiasBeneficiadas,
    articulos,
  };
}

export const MOCK_LOTES: Lote[] = [
  lote(
    'lote-041',
    '#PX-LOT-2026-041',
    fechaUTC(2026, 10, 18),
    'Arroz, Avena y Menestras',
    'Arroz superior y lentejas serranas',
    'Cáritas Huancayo',
    'entregado',
    45,
    [
      articulo('a-041-1', 'Arroz, Avena y Menestras', 'Arroz superior (saco 50 kg)', 60, 'Kg', 1, fechaUTC(2027, 5, 15)),
      articulo('a-041-2', 'Arroz, Avena y Menestras', 'Lenteja serrana (bolsa 1 kg)', 40, 'Kg', 1, fechaUTC(2027, 3, 20)),
    ],
  ),
  lote(
    'lote-042',
    '#PX-LOT-2026-042',
    fechaUTC(2026, 10, 20),
    'Leche evaporada y Suplementos de bebé',
    'Leche evaporada y fórmula infantil',
    'Comedor Popular "Santa Rosa"',
    'preparacion',
    30,
    [
      articulo('a-042-1', 'Leche evaporada y Suplementos de bebé', 'Leche evaporada entera (lata 400 g)', 48, 'Unid.', 0.4, fechaUTC(2027, 1, 10)),
      articulo('a-042-2', 'Leche evaporada y Suplementos de bebé', 'Fórmula infantil etapa 2 (bolsa 800 g)', 12, 'Paq.', 0.8, fechaUTC(2026, 11, 28)),
    ],
  ),
  lote(
    'lote-043',
    '#PX-LOT-2026-043',
    fechaUTC(2026, 10, 22),
    'Galletas y Cereales',
    'Galletas fortificadas y avena',
    'Hogar de Niños San José',
    'pendiente',
    20,
    [
      articulo('a-043-1', 'Galletas y Cereales', 'Galletas fortificadas de quinua (paquete)', 30, 'Paq.', 0.5, fechaUTC(2026, 11, 5)),
      articulo('a-043-2', 'Galletas y Cereales', 'Avena instantánea (bolsa 1 kg)', 10, 'Kg', 1, fechaUTC(2027, 0, 15)),
    ],
  ),
  lote(
    'lote-044',
    '#PX-LOT-2026-044',
    fechaUTC(2026, 10, 23),
    'Conservas de Pescado & Aceites',
    'Atún en aceite y aceite vegetal',
    'Cáritas Huancayo',
    'entregado',
    60,
    [
      articulo('a-044-1', 'Conservas de Pescado & Aceites', 'Atún en aceite (lata 170 g)', 72, 'Unid.', 0.17, fechaUTC(2028, 2, 12)),
      articulo('a-044-2', 'Conservas de Pescado & Aceites', 'Aceite vegetal (botella 1 L)', 24, 'Unid.', 0.9, fechaUTC(2027, 7, 8)),
    ],
  ),
  lote(
    'lote-045',
    '#PX-LOT-2026-045',
    fechaUTC(2026, 10, 24),
    'Fideos y Sémolas Diversas',
    'Fideos y sémola de trigo',
    'Comedor San José',
    'preparacion',
    18,
    [
      articulo('a-045-1', 'Fideos y Sémolas Diversas', 'Fideos tallarín (bolsa 500 g)', 50, 'Kg', 1, fechaUTC(2027, 4, 30)),
      articulo('a-045-2', 'Fideos y Sémolas Diversas', 'Sémola de trigo (bolsa 1 kg)', 15, 'Kg', 1, fechaUTC(2026, 11, 10)),
    ],
  ),
];

export const MOCK_USUARIOS: Usuario[] = [
  {
    id: 'A001',
    nombre: 'Prof. Taipe',
    telefono: '+51 999 999 999',
    correo: 'pastoral@sanpiox.edu.pe',
    rol: 'administrativo',
    activo: true,
  },
  {
    id: 'A002',
    nombre: 'Hna. Teresa Gómez',
    telefono: '+51 988 777 666',
    correo: 'teresa.gomez@sanpiox.edu.pe',
    rol: 'administrativo',
    activo: true,
  },
  {
    id: 'U001',
    nombre: 'Familia Quispe',
    telefono: '+51 964 123 456',
    correo: 'donante@sanpiox.edu.pe',
    rol: 'donante',
    activo: true,
  },
  {
    id: 'U002',
    nombre: 'Familia Huamán',
    telefono: '+51 955 321 789',
    correo: 'familia.huaman@correo.com',
    rol: 'donante',
    activo: true,
  },
  {
    id: 'U003',
    nombre: 'Empresa Andina S.A.C.',
    telefono: '+51 944 555 222',
    correo: 'donaciones@empresaandina.pe',
    rol: 'donante',
    activo: false,
  },
];

export const METAS_BASE: MetaDonacionBase[] = [
  {
    id: 'meta-arroz',
    categoria: 'Arroz, Avena y Menestras',
    icono: 'bi-flower1',
    metaKg: 500,
    color: 'naranjaoscuro',
  },
  {
    id: 'meta-conservas',
    categoria: 'Conservas de Pescado & Aceites',
    icono: 'bi-tsunami',
    metaKg: 500,
    color: 'azuloscuro',
  },
  {
    id: 'meta-leche',
    categoria: 'Leche evaporada y Suplementos de bebé',
    icono: 'bi-person-arms-up',
    metaKg: 500,
    color: 'verdeoscuro',
  },
  {
    id: 'meta-fideos',
    categoria: 'Fideos y Sémolas Diversas',
    icono: 'bi-cup-hot-fill',
    metaKg: 500,
    color: 'moradooscuro',
  },
];

export const CREDENCIALES_DEMO: Record<
  RolUsuario,
  { correo: string; password: string; usuarioId: string }
> = {
  administrativo: {
    correo: 'pastoral@sanpiox.edu.pe',
    password: 'admin123',
    usuarioId: 'A001',
  },
  donante: {
    correo: 'donante@sanpiox.edu.pe',
    password: 'donante123',
    usuarioId: 'U001',
  },
};

export const MOCK_SOLICITUDES: SolicitudRecuperacion[] = [
  {
    id: 'SOL-001',
    correo: 'familia.huaman@correo.com',
    fecha: fechaUTC(2026, 10, 23, 9, 30),
    atendida: false,
  },
];
