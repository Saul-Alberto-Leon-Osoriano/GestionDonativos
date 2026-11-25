import { DecimalPipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { LoteService } from '../../core/services/lote.service';
import { EstadoLote, Lote } from '../../core/models/lote.model';
import { formatearFecha } from '../../core/models/donativo.model';
import { mensajeErrorApi } from '../../core/utils/api.utils';
import { descargarArchivo } from '../../shared/download';

@Component({
  imports: [DecimalPipe],
  selector: 'app-gestion-lotes',
  styleUrl: './gestion-lotes.css',
  templateUrl: './gestion-lotes.html',
})
export class GestionLotes {
  readonly lotesService = inject(LoteService);
  readonly seleccionado = signal<Lote | null>(null);
  readonly error = signal<string | null>(null);

  readonly lotes = this.lotesService.lotesPaginados;

  estadoTexto(estado: EstadoLote): string {
    switch (estado) {
      case 'entregado':
        return 'Entregado';
      case 'preparacion':
        return 'En preparación';
      default:
        return 'Pendiente';
    }
  }

  estadoIcono(estado: EstadoLote): string {
    switch (estado) {
      case 'entregado':
        return 'bi-check-circle-fill';
      case 'preparacion':
        return 'bi-hourglass-split';
      default:
        return 'bi-clock-fill';
    }
  }

  estadoClase(estado: EstadoLote): string {
    return `estado-${estado}`;
  }

  fecha(fecha: Date | null): string {
    return formatearFecha(fecha);
  }

  buscar(evento: Event): void {
    const valor = (evento.target as HTMLInputElement).value;
    this.lotesService.buscar(valor);
  }

  verDetalle(lote: Lote): void {
    this.seleccionado.set(lote);
  }

  cerrarDetalle(): void {
    this.seleccionado.set(null);
  }

  async exportar(): Promise<void> {
    this.error.set(null);

    try {
      const contenido = await this.lotesService.exportarCsv();
      descargarArchivo(
        `lotes-${new Date().toISOString().slice(0, 10)}.csv`,
        contenido,
      );
    } catch (error) {
      this.error.set(mensajeErrorApi(error));
    }
  }
}
