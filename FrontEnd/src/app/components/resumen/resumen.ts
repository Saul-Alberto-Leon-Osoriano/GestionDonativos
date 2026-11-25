import { DecimalPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { TransparenciaService } from '../../core/services/transparencia.service';

@Component({
  imports: [DecimalPipe],
  selector: 'app-resumen',
  styleUrl: './resumen.css',
  templateUrl: './resumen.html',
})
export class Resumen {
  readonly transparencia = inject(TransparenciaService);
  readonly estadisticas = this.transparencia.estadisticas;
}
