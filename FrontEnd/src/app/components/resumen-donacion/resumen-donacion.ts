import { DecimalPipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { DonativoDraftService } from '../../core/services/donativo-draft.service';
import { Lote } from '../../core/models/lote.model';
import { mensajeErrorApi } from '../../core/utils/api.utils';

@Component({
  imports: [DecimalPipe],
  selector: 'app-resumen-donacion',
  styleUrl: './resumen-donacion.css',
  templateUrl: './resumen-donacion.html',
})
export class ResumenDonacion {
  readonly draft = inject(DonativoDraftService);
  private readonly router = inject(Router);

  readonly resumen = this.draft.resumen;
  readonly mensaje = signal<string | null>(null);
  readonly error = signal<string | null>(null);
  readonly ultimoLote = signal<Lote | null>(null);

  async guardar(imprimir = false): Promise<void> {
    this.mensaje.set(null);
    this.error.set(null);

    if (this.draft.form().invalid()) {
      this.draft.form().markAsTouched();
      this.error.set('Revisa los campos marcados antes de guardar el ingreso.');
      return;
    }

    try {
      const lote = await this.draft.guardar();
      this.ultimoLote.set(lote);
      this.mensaje.set(
        `Ingreso guardado correctamente con el código ${lote.codigo}.`,
      );

      if (imprimir && typeof window !== 'undefined') {
        setTimeout(() => window.print(), 150);
      }
    } catch (error) {
      this.error.set(mensajeErrorApi(error));
    }
  }

  irAlPanel(): void {
    void this.router.navigateByUrl('/panel-control');
  }
}
