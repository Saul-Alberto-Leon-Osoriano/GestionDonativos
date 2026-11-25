import { DecimalPipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LoteService } from '../../core/services/lote.service';
import { mensajeErrorApi } from '../../core/utils/api.utils';
import { descargarArchivo } from '../../shared/download';

@Component({
  imports: [DecimalPipe, RouterLink],
  selector: 'app-targetas-superiores',
  styleUrl: './targetas-superiores.css',
  templateUrl: './targetas-superiores.html',
})
export class TargetasSuperiores {
  private readonly loteService = inject(LoteService);

  readonly kpis = this.loteService.kpis;
  readonly error = signal<string | null>(null);
  readonly enPreparacion = computed(
    () =>
      this.loteService
        .lotes()
        .filter((lote) => lote.estado === 'preparacion').length,
  );
  readonly instituciones = computed(
    () => new Set(this.loteService.lotes().map((lote) => lote.destino)).size,
  );

  async exportarReporte(): Promise<void> {
    this.error.set(null);

    try {
      const contenido = await this.loteService.exportarCsv();
      descargarArchivo(
        `reporte-lotes-${new Date().toISOString().slice(0, 10)}.csv`,
        contenido,
      );
    } catch (error) {
      this.error.set(mensajeErrorApi(error));
    }
  }
}
