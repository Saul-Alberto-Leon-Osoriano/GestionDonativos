import { Component, inject } from '@angular/core';
import { TransparenciaService } from '../../core/services/transparencia.service';
import { HitoDonacion } from '../../core/models/transparencia.model';

@Component({
  imports: [],
  selector: 'app-linea-tiempo',
  styleUrl: './linea-tiempo.css',
  templateUrl: './linea-tiempo.html',
})
export class LineaTiempo {
  readonly transparencia = inject(TransparenciaService);
  readonly hitos = this.transparencia.hitos;

  fecha(fecha: Date): string {
    return new Intl.DateTimeFormat('es-PE', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      timeZone: 'UTC',
    }).format(fecha);
  }

  esRecepcionado(hito: HitoDonacion): boolean {
    return hito.estado === 'recepcionado';
  }
}
