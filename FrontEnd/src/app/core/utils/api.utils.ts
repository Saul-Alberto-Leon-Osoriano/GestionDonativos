import { HttpErrorResponse } from '@angular/common/http';
import { ArticuloDonacion } from '../models/donativo.model';
import { AlertaVencimiento, Lote } from '../models/lote.model';
import { HitoDonacion } from '../models/transparencia.model';

type FechaApi = string | Date | null | undefined;

/**
 * Convierte las fechas ISO 8601 que devuelve FastAPI a `Date`.
 * El backend siempre responde en UTC; el frontend mantiene ese criterio.
 */
export function parsearFechaApi(valor: FechaApi): Date {
  if (valor instanceof Date) {
    return valor;
  }

  const fecha = new Date(valor ?? '');
  return Number.isNaN(fecha.getTime()) ? new Date() : fecha;
}

export function parsearFechaOpcionalApi(valor: FechaApi): Date | null {
  if (!valor) {
    return null;
  }

  const fecha = parsearFechaApi(valor);
  return Number.isNaN(fecha.getTime()) ? null : fecha;
}

export function hidratarArticulo(articulo: ArticuloDonacion): ArticuloDonacion {
  return {
    ...articulo,
    fechaVencimiento: parsearFechaOpcionalApi(
      articulo.fechaVencimiento as unknown as FechaApi,
    ),
  };
}

export function hidratarLote(lote: Lote): Lote {
  return {
    ...lote,
    fechaIngreso: parsearFechaApi(lote.fechaIngreso as unknown as FechaApi),
    articulos: lote.articulos.map(hidratarArticulo),
  };
}

export function hidratarAlerta(alerta: AlertaVencimiento): AlertaVencimiento {
  return {
    ...alerta,
    fechaVencimiento: parsearFechaApi(
      alerta.fechaVencimiento as unknown as FechaApi,
    ),
  };
}

export function hidratarHito(hito: HitoDonacion): HitoDonacion {
  return {
    ...hito,
    fecha: parsearFechaApi(hito.fecha as unknown as FechaApi),
  };
}

/**
 * Extrae el mensaje en español que envía FastAPI (`detail` / `errores`).
 */
export function mensajeErrorApi(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    const cuerpo: unknown = error.error;

    if (typeof cuerpo === 'string' && cuerpo.trim()) {
      return cuerpo;
    }

    if (cuerpo && typeof cuerpo === 'object') {
      const detalle = (cuerpo as { detail?: unknown }).detail;
      if (typeof detalle === 'string' && detalle.trim()) {
        return detalle;
      }

      const errores = (cuerpo as { errores?: unknown }).errores;
      if (Array.isArray(errores)) {
        const mensajes = errores
          .map((item: unknown) => {
            if (!item || typeof item !== 'object') {
              return String(item);
            }

            const campo = (item as { campo?: unknown }).campo;
            const mensaje = (item as { mensaje?: unknown }).mensaje;
            const partes = [campo, mensaje]
              .filter((parte) => typeof parte === 'string' && parte.trim())
              .map(String);
            return partes.join(': ');
          })
          .filter((mensaje) => mensaje.length > 0);

        if (mensajes.length > 0) {
          return mensajes.join(' ');
        }
      }
    }

    if (error.status === 0) {
      return 'No se pudo conectar con el servidor. Verifica que el backend esté en ejecución.';
    }

    return error.message || `La solicitud falló con el código ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Ocurrió un error inesperado.';
}
