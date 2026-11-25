import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import {
  computed,
  inject,
  Injectable,
  PLATFORM_ID,
  signal,
} from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  EstadisticasPublicas,
  HitoDonacion,
  MetaDonacion,
} from '../models/transparencia.model';
import { hidratarHito, mensajeErrorApi } from '../utils/api.utils';

const ESTADISTICAS_VACIAS: EstadisticasPublicas = {
  totalKg: 0,
  totalLotes: 0,
  totalFamilias: 0,
};

@Injectable({ providedIn: 'root' })
export class TransparenciaService {
  private readonly http = inject(HttpClient);
  private readonly esNavegador = isPlatformBrowser(inject(PLATFORM_ID));
  private readonly apiURL = environment.apiURL;

  private readonly metasState = signal<MetaDonacion[]>([]);
  private readonly hitosState = signal<HitoDonacion[]>([]);
  private readonly estadisticasState = signal<EstadisticasPublicas>({
    ...ESTADISTICAS_VACIAS,
  });
  private readonly errorState = signal<string | null>(null);

  readonly metas = this.metasState.asReadonly();
  readonly hitos = this.hitosState.asReadonly();
  readonly estadisticas = this.estadisticasState.asReadonly();
  readonly error = this.errorState.asReadonly();

  readonly metaGeneralKg = computed(() =>
    this.metasState().reduce((total, meta) => total + meta.metaKg, 0),
  );

  constructor() {
    void this.recargar();
  }

  async recargar(): Promise<void> {
    if (!this.esNavegador) {
      return;
    }

    this.errorState.set(null);

    const [metas, hitos, estadisticas] = await Promise.allSettled([
      firstValueFrom(
        this.http.get<MetaDonacion[]>(
          `${this.apiURL}/api/transparencia/metas`,
        ),
      ),
      firstValueFrom(
        this.http.get<HitoDonacion[]>(
          `${this.apiURL}/api/transparencia/hitos`,
        ),
      ),
      firstValueFrom(
        this.http.get<EstadisticasPublicas>(
          `${this.apiURL}/api/transparencia/estadisticas`,
        ),
      ),
    ]);

    if (metas.status === 'fulfilled') {
      this.metasState.set(metas.value);
    }

    if (hitos.status === 'fulfilled') {
      this.hitosState.set(hitos.value.map(hidratarHito));
    }

    if (estadisticas.status === 'fulfilled') {
      this.estadisticasState.set(estadisticas.value);
    }

    const fallo = [metas, hitos, estadisticas].find(
      (resultado) => resultado.status === 'rejected',
    );

    if (fallo?.status === 'rejected') {
      this.errorState.set(mensajeErrorApi(fallo.reason));
    }
  }
}
