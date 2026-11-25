import { Component, computed, inject } from '@angular/core';
import { FormField } from '@angular/forms/signals';
import { DonativoDraftService } from '../../core/services/donativo-draft.service';
import { TIPOS_DONANTE } from '../../core/models/donativo.model';
import { FormError } from '../../shared/form-error/form-error';

@Component({
  imports: [FormField, FormError],
  selector: 'app-datos-donante',
  styleUrl: './datos-donante.css',
  templateUrl: './datos-donante.html',
})
export class DatosDonante {
  readonly draft = inject(DonativoDraftService);
  readonly tiposDonante = TIPOS_DONANTE;
  readonly esAnonimo = computed(
    () => this.draft.modelo().donante.tipo === 'anonimo',
  );
}
