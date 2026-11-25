import { Component, computed, inject } from '@angular/core';
import { FieldTree, FormField } from '@angular/forms/signals';
import { DonativoDraftService } from '../../core/services/donativo-draft.service';
import {
  ArticuloDonacion,
  CATEGORIAS_ALIMENTO,
  diasHasta,
  UNIDADES_MEDIDA,
} from '../../core/models/donativo.model';
import { FormError } from '../../shared/form-error/form-error';

@Component({
  imports: [FormField, FormError],
  selector: 'app-detalles-donacion',
  styleUrl: './detalles-donacion.css',
  templateUrl: './detalles-donacion.html',
})
export class DetallesDonacion {
  readonly draft = inject(DonativoDraftService);
  readonly categorias = CATEGORIAS_ALIMENTO;
  readonly unidades = UNIDADES_MEDIDA;

  readonly campos = computed<FieldTree<ArticuloDonacion>[]>(() =>
    this.draft
      .modelo()
      .articulos.map(
        (_, indice) =>
          (
            this.draft.form.articulos as unknown as FieldTree<ArticuloDonacion>[]
          )[indice],
      ),
  );

  esPorVencer(articulo: ArticuloDonacion): boolean {
    if (!articulo.fechaVencimiento) {
      return false;
    }

    const dias = diasHasta(articulo.fechaVencimiento);
    return dias >= 0 && dias <= 30;
  }

  quitar(id: string): void {
    this.draft.quitarArticulo(id);
  }
}
