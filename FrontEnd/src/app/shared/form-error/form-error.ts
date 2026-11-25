import { Component, computed, input } from '@angular/core';

export interface CampoEstado {
  touched(): boolean;
  invalid(): boolean;
  errors(): readonly { message?: string }[];
}

@Component({
  selector: 'app-form-error',
  template: `
    @if (campo().touched() && campo().invalid()) {
      <div class="invalid-feedback d-block">{{ mensaje() }}</div>
    }
  `,
})
export class FormError {
  readonly campo = input.required<CampoEstado>();

  protected readonly mensaje = computed(
    () => this.campo().errors()[0]?.message ?? 'Revisa este campo.',
  );
}
