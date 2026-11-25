import { Component, computed, inject } from '@angular/core';
import { FormField } from '@angular/forms/signals';
import { DonativoDraftService } from '../../core/services/donativo-draft.service';
import { LoteService } from '../../core/services/lote.service';
import { FormError } from '../../shared/form-error/form-error';

@Component({
  imports: [FormField, FormError],
  selector: 'app-trazabilidad-donacion',
  styleUrl: './trazabilidad-donacion.css',
  templateUrl: './trazabilidad-donacion.html',
})
export class TrazabilidadDonacion {
  readonly draft = inject(DonativoDraftService);
  private readonly loteService = inject(LoteService);

  readonly codigoLote = this.loteService.siguienteCodigo;
  readonly fechaIngreso = new Date();
  readonly fechaFormateada = computed(() =>
    new Intl.DateTimeFormat('es-PE', {
      weekday: 'long',
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    }).format(this.fechaIngreso),
  );
  readonly horaFormateada = computed(() =>
    new Intl.DateTimeFormat('es-PE', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(this.fechaIngreso),
  );
}
