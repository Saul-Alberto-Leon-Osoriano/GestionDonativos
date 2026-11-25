import { DecimalPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { TransparenciaService } from '../../core/services/transparencia.service';
import { MetaDonacion } from '../../core/models/transparencia.model';

@Component({
  imports: [DecimalPipe],
  selector: 'app-metas-donacion',
  styleUrl: './metas-donacion.css',
  templateUrl: './metas-donacion.html',
})
export class MetasDonacion {
  readonly transparencia = inject(TransparenciaService);
  readonly metas = this.transparencia.metas;
  readonly metaGeneral = this.transparencia.metaGeneralKg;

  porcentaje(meta: MetaDonacion): number {
    if (meta.metaKg <= 0) {
      return 0;
    }
    return Math.min(100, Math.round((meta.recolectadoKg / meta.metaKg) * 100));
  }

  claseIcono(color: string): string {
    return color.replace('oscuro', '');
  }

  claseTexto(color: string): string {
    return `${color}--letra`;
  }
}
