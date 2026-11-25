import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import {
  computed,
  inject,
  Injectable,
  PLATFORM_ID,
  signal,
} from '@angular/core';
import { form } from '@angular/forms/signals';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { donativoSchema } from '../forms/donativo.schema';
import {
  ArticuloDonacion,
  calcularResumenDonativo,
  crearArticuloVacio,
  crearDonativoVacio,
  DonativoDraft,
} from '../models/donativo.model';
import { Lote } from '../models/lote.model';
import { hidratarLote } from '../utils/api.utils';
import { LoteService } from './lote.service';

@Injectable({ providedIn: 'root' })
export class DonativoDraftService {
  private readonly http = inject(HttpClient);
  private readonly esNavegador = isPlatformBrowser(inject(PLATFORM_ID));
  private readonly loteService = inject(LoteService);
  private readonly apiURL = environment.apiURL;

  readonly modelo = signal<DonativoDraft>(crearDonativoVacio());
  readonly form = form(this.modelo, donativoSchema);
  readonly resumen = computed(() => calcularResumenDonativo(this.modelo()));
  readonly puedeGuardar = computed(() => this.form().valid());
  readonly guardando = signal(false);

  agregarArticulo(): void {
    this.modelo.update((draft) => ({
      ...draft,
      articulos: [...draft.articulos, crearArticuloVacio()],
    }));
  }

  quitarArticulo(id: string): void {
    this.modelo.update((draft) => {
      if (draft.articulos.length <= 1) {
        return draft;
      }

      return {
        ...draft,
        articulos: draft.articulos.filter((articulo) => articulo.id !== id),
      };
    });
  }

  actualizarArticulo(id: string, cambios: Partial<ArticuloDonacion>): void {
    this.modelo.update((draft) => ({
      ...draft,
      articulos: draft.articulos.map((articulo) =>
        articulo.id === id ? { ...articulo, ...cambios } : articulo,
      ),
    }));
  }

  limpiar(): void {
    this.modelo.set(crearDonativoVacio());
    this.form().reset();
  }

  async guardar(): Promise<Lote> {
    if (!this.esNavegador) {
      throw new Error('El registro de donativos solo está disponible en el navegador.');
    }

    this.guardando.set(true);

    try {
      const respuesta = await firstValueFrom(
        this.http.post<Lote>(
          `${this.apiURL}/api/donativos`,
          this.modelo(),
        ),
      );

      const lote = hidratarLote(respuesta);
      this.limpiar();
      void this.loteService.recargar();
      return lote;
    } finally {
      this.guardando.set(false);
    }
  }
}
