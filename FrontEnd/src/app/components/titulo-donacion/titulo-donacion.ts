import { Component, inject } from '@angular/core';
import { DonativoDraftService } from '../../core/services/donativo-draft.service';

@Component({
  imports: [],
  selector: 'app-titulo-donacion',
  styleUrl: './titulo-donacion.css',
  templateUrl: './titulo-donacion.html',
})
export class TituloDonacion {
  private readonly draft = inject(DonativoDraftService);

  limpiar(): void {
    this.draft.limpiar();
  }
}
