import { HttpClient, HttpParams } from '@angular/common/http';
import {
  computed,
  inject,
  Injectable,
  PLATFORM_ID,
  signal,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  AlertaVencimiento,
  EstadoLote,
  KpisInventario,
  Lote,
  RespuestaPaginada,
} from '../models/lote.model';
import {
  hidratarAlerta,
  hidratarLote,
  mensajeErrorApi,
} from '../utils/api.utils';

const KPIS_VACIOS: KpisInventario = {
  totalAcopiado: 0,
  lotesActivos: 0,
  lotesEntregados: 0,
  articulosCriticos: 0,
};

@Injectable({ providedIn: 'root' })
export class LoteService {
  private readonly http = inject(HttpClient);
  private readonly esNavegador = isPlatformBrowser(inject(PLATFORM_ID));
  private readonly apiURL = environment.apiURL;

  private readonly lotesState = signal<Lote[]>([]);
  private readonly totalState = signal(0);
  private readonly kpisState = signal<KpisInventario>({ ...KPIS_VACIOS });
  private readonly alertasState = signal<AlertaVencimiento[]>([]);
  private readonly cargandoState = signal(false);
  private readonly errorState = signal<string | null>(null);

  private solicitudActual = 0;

  readonly lotes = this.lotesState.asReadonly();
  readonly lotesFiltrados = this.lotesState.asReadonly();
  readonly lotesPaginados = this.lotesState.asReadonly();
  readonly total = this.totalState.asReadonly();
  readonly kpis = this.kpisState.asReadonly();
  readonly alertas = this.alertasState.asReadonly();
  readonly cargando = this.cargandoState.asReadonly();
  readonly error = this.errorState.asReadonly();

  readonly busqueda = signal('');
  readonly pagina = signal(1);
  readonly porPagina = 5;

  readonly totalPaginas = computed(() =>
    Math.max(1, Math.ceil(this.totalState() / this.porPagina)),
  );

  readonly paginas = computed(() =>
    Array.from({ length: this.totalPaginas() }, (_, indice) => indice + 1),
  );

  readonly siguienteCodigo = computed(() => {
    const anio = new Date().getFullYear();
    const maximo = this.lotesState().reduce((max, lote) => {
      const coincidencia = lote.codigo.match(/(\d+)$/);
      const numero = coincidencia ? Number(coincidencia[1]) : 0;
      return Math.max(max, Number.isNaN(numero) ? 0 : numero);
    }, 0);

    return `#PX-LOT-${anio}-${String(maximo + 1).padStart(3, '0')}`;
  });

  constructor() {
    void this.recargar();
  }

  async recargar(): Promise<void> {
    if (!this.esNavegador) {
      return;
    }

    const solicitud = ++this.solicitudActual;
    this.cargandoState.set(true);
    this.errorState.set(null);

    try {
      const [pagina, kpis, alertas] = await Promise.all([
        firstValueFrom(
          this.http.get<RespuestaPaginada<Lote>>(`${this.apiURL}/api/lotes`, {
            params: this.crearParametros(true),
          }),
        ),
        firstValueFrom(
          this.http.get<KpisInventario>(`${this.apiURL}/api/lotes/kpis`),
        ),
        firstValueFrom(
          this.http.get<AlertaVencimiento[]>(
            `${this.apiURL}/api/lotes/alertas`,
          ),
        ),
      ]);

      if (solicitud !== this.solicitudActual) {
        return;
      }

      this.lotesState.set(pagina.items.map(hidratarLote));
      this.totalState.set(pagina.total);
      this.kpisState.set(kpis);
      this.alertasState.set(alertas.map(hidratarAlerta));
      this.pagina.set(pagina.pagina);
    } catch (error) {
      if (solicitud !== this.solicitudActual) {
        return;
      }

      this.errorState.set(mensajeErrorApi(error));
    } finally {
      if (solicitud === this.solicitudActual) {
        this.cargandoState.set(false);
      }
    }
  }

  buscar(termino: string): void {
    this.busqueda.set(termino);
    this.pagina.set(1);
    void this.recargar();
  }

  cambiarPagina(pagina: number): void {
    const destino = Math.min(Math.max(1, pagina), this.totalPaginas());
    if (destino === this.pagina()) {
      return;
    }

    this.pagina.set(destino);
    void this.recargar();
  }

  async priorizarLote(loteId: string): Promise<void> {
    if (!this.esNavegador) {
      return;
    }

    await this.priorizarLoteSinRecargar(loteId);
    await this.recargar();
  }

  async generarDespachoUrgente(): Promise<number> {
    if (!this.esNavegador) {
      return 0;
    }

    const ids = [...new Set(this.alertasState().map((alerta) => alerta.loteId))];
    const resultados = await Promise.allSettled(
      ids.map((id) => this.priorizarLoteSinRecargar(id)),
    );

    await this.recargar();

    return resultados.filter(
      (resultado) =>
        resultado.status === 'fulfilled' && resultado.value === true,
    ).length;
  }

  async exportarCsv(): Promise<string> {
    if (!this.esNavegador) {
      return '';
    }

    const contenido = await firstValueFrom(
      this.http.get(`${this.apiURL}/api/lotes/exportar.csv`, {
        params: this.crearParametros(false),
        responseType: 'text',
      }),
    );

    return contenido.replace(/^\uFEFF/, '');
  }

  private crearParametros(incluirPaginacion: boolean): HttpParams {
    let parametros = new HttpParams();
    const termino = this.busqueda().trim();

    if (termino) {
      parametros = parametros.set('termino', termino);
    }

    if (incluirPaginacion) {
      parametros = parametros
        .set('pagina', String(this.pagina()))
        .set('tamanoPagina', String(this.porPagina));
    }

    return parametros;
  }

  private async priorizarLoteSinRecargar(loteId: string): Promise<boolean> {
    const lote = await this.obtenerLote(loteId);
    if (lote.estado === 'entregado') {
      return false;
    }

    await this.cambiarEstado(loteId, 'preparacion');
    return true;
  }

  private async obtenerLote(loteId: string): Promise<Lote> {
    const lote = this.lotesState().find((item) => item.id === loteId);
    if (lote) {
      return lote;
    }

    const respuesta = await firstValueFrom(
      this.http.get<Lote>(`${this.apiURL}/api/lotes/${loteId}`),
    );
    return hidratarLote(respuesta);
  }

  private async cambiarEstado(
    loteId: string,
    estado: EstadoLote,
  ): Promise<Lote> {
    const respuesta = await firstValueFrom(
      this.http.put<Lote>(`${this.apiURL}/api/lotes/${loteId}/estado`, {
        estado,
      }),
    );
    return hidratarLote(respuesta);
  }
}
