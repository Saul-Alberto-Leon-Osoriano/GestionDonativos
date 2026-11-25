import {
  applyEach,
  maxLength,
  min,
  minDate,
  minLength,
  pattern,
  required,
  schema,
} from '@angular/forms/signals';
import { DonativoDraft, hoyUTC } from '../models/donativo.model';

export const donativoSchema = schema<DonativoDraft>((path) => {
  const esAnonimo = ({ valueOf }: { valueOf: (campo: typeof path.donante.tipo) => unknown }) =>
    valueOf(path.donante.tipo) === 'anonimo';

  required(path.donante.nombre, {
    message: 'Ingresa el nombre del donante o la razón social.',
    when: (contexto) => !esAnonimo(contexto),
  });
  required(path.donante.documento, {
    message: 'Ingresa el DNI o RUC de contacto.',
    when: (contexto) => !esAnonimo(contexto),
  });
  required(path.donante.telefono, {
    message: 'Ingresa un teléfono o WhatsApp de contacto.',
    when: (contexto) => !esAnonimo(contexto),
  });
  pattern(path.donante.telefono, /^[+0-9 ()-]{6,}$/, {
    message: 'Usa solo números, espacios, paréntesis, guiones o el prefijo +.',
    when: ({ valueOf }) => valueOf(path.donante.telefono).trim().length > 0,
  });

  required(path.destino, {
    message: 'Indica el destino solidario del lote.',
  });

  maxLength(path.observaciones, 500, {
    message: 'Las observaciones no deben superar los 500 caracteres.',
  });

  minLength(path.articulos, 1, {
    message: 'Agrega al menos un artículo a la donación.',
  });

  applyEach(path.articulos, (articulo) => {
    required(articulo.categoria, {
      message: 'Selecciona o escribe la categoría del alimento.',
    });
    required(articulo.descripcion, {
      message: 'Describe el producto donado.',
    });
    min(articulo.cantidad, 1, {
      message: 'La cantidad debe ser mayor o igual a 1.',
    });
    required(articulo.pesoUnitarioKg, {
      message: 'Indica el peso por unidad para calcular el peso neto.',
    });
    min(articulo.pesoUnitarioKg, 0.01, {
      message: 'El peso unitario debe ser mayor que 0 kg.',
    });
    required(articulo.fechaVencimiento, {
      message: 'Selecciona la fecha de vencimiento.',
    });
    minDate(articulo.fechaVencimiento, () => hoyUTC(), {
      message: 'La fecha de vencimiento no puede ser anterior a hoy.',
    });
  });
});
