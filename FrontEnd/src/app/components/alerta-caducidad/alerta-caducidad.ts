import { Component, computed, inject, signal } from '@angular/core';
import { LoteService } from '../../core/services/lote.service';
import { AlertaVencimiento } from '../../core/models/lote.model';
import { formatearFecha } from '../../core/models/donativo.model';
import { mensajeErrorApi } from '../../core/utils/api.utils';

@Component({
  imports: [],
  selector: 'app-alerta-caducidad',
  styleUrl: './alerta-caducidad.css',
  templateUrl: './alerta-caducidad.html',
})
export class AlertaCaducidad {
  private readonly loteService = inject(LoteService);

  readonly alertas = computed(() => this.loteService.alertas().slice(0, 4));
  readonly total = this.loteService.alertas;
  readonly mensaje = signal<string | null>(null);
  readonly accionEnCurso = signal(false);

  fecha(fecha: Date): string {
    return formatearFecha(fecha);
  }

  async priorizar(alerta: AlertaVencimiento): Promise<void> {
    if (this.accionEnCurso()) {
      return;
    }

    this.accionEnCurso.set(true);
    this.mensaje.set(null);

    try {
      await this.loteService.priorizarLote(alerta.loteId);
      this.mensaje.set(
        `El lote ${alerta.lote} pasó a preparación prioritaria.`,
      );
    } catch (error) {
      this.mensaje.set(mensajeErrorApi(error));
    } finally {
      this.accionEnCurso.set(false);
    }
  }

  async generarDespachoUrgente(): Promise<void> {
    if (this.accionEnCurso()) {
      return;
    }

    this.accionEnCurso.set(true);
    this.mensaje.set(null);

    try {
      const cantidad = await this.loteService.generarDespachoUrgente();
      this.mensaje.set(
        cantidad > 0
          ? `${cantidad} lote(s) con artículos críticos fueron marcados para despacho urgente.`
          : 'No hay lotes pendientes con artículos críticos.',
      );
    } catch (error) {
      this.mensaje.set(mensajeErrorApi(error));
    } finally {
      this.accionEnCurso.set(false);
    }
  }
}
