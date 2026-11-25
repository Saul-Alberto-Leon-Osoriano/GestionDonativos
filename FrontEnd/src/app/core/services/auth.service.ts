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
  CLAVE_SESION,
  CLAVE_TOKEN,
  Credenciales,
  RespuestaLogin,
  SesionUsuario,
  SolicitudRecuperacion,
} from '../models/auth.model';
import { mensajeErrorApi } from '../utils/api.utils';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly platformId = inject(PLATFORM_ID);
  private readonly apiURL = environment.apiURL;

  readonly sesion = signal<SesionUsuario | null>(this.cargarSesion());
  private readonly tokenState = signal<string | null>(this.cargarToken());
  private readonly errorState = signal<string | null>(null);
  readonly solicitudes = signal<SolicitudRecuperacion[]>([]);

  readonly token = this.tokenState.asReadonly();
  readonly error = this.errorState.asReadonly();

  readonly estaAutenticado = computed(() => {
    const token = this.tokenState();
    return !!token && !this.tokenExpirado(token) && this.sesion() !== null;
  });

  readonly esAdministrativo = computed(
    () => this.sesion()?.rol === 'administrativo',
  );

  readonly solicitudesPendientes = computed(
    () => this.solicitudes().filter((solicitud) => !solicitud.atendida).length,
  );

  async login(credenciales: Credenciales): Promise<boolean> {
    this.errorState.set(null);

    try {
      const respuesta = await firstValueFrom(
        this.http.post<RespuestaLogin>(`${this.apiURL}/api/auth/login`, {
          correo: credenciales.correo.trim().toLowerCase(),
          password: credenciales.password,
        }),
      );

      const sesion = respuesta.usuario;
      this.sesion.set(sesion);
      this.tokenState.set(respuesta.accessToken);
      this.guardarSesion(sesion, respuesta.accessToken, credenciales.recordar);
      return true;
    } catch (error) {
      this.errorState.set(mensajeErrorApi(error));
      this.limpiarSesion();
      return false;
    }
  }

  logout(): void {
    this.limpiarSesion();
  }

  async solicitarRecuperacion(correo: string): Promise<boolean> {
    this.errorState.set(null);

    try {
      await firstValueFrom(
        this.http.post(`${this.apiURL}/api/auth/recuperacion`, {
          correo: correo.trim().toLowerCase(),
        }),
      );
      return true;
    } catch (error) {
      this.errorState.set(mensajeErrorApi(error));
      return false;
    }
  }

  marcarSolicitudAtendida(id: string): void {
    this.solicitudes.update((solicitudes) =>
      solicitudes.map((solicitud) =>
        solicitud.id === id ? { ...solicitud, atendida: true } : solicitud,
      ),
    );
  }

  private limpiarSesion(): void {
    this.sesion.set(null);
    this.tokenState.set(null);
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem(CLAVE_SESION);
      localStorage.removeItem(CLAVE_TOKEN);
      sessionStorage.removeItem(CLAVE_SESION);
      sessionStorage.removeItem(CLAVE_TOKEN);
    }
  }

  private guardarSesion(
    sesion: SesionUsuario,
    token: string,
    recordar: boolean,
  ): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    this.limpiarAlmacenamiento();
    const almacen = recordar ? localStorage : sessionStorage;
    almacen.setItem(CLAVE_SESION, JSON.stringify(sesion));
    almacen.setItem(CLAVE_TOKEN, token);
  }

  private cargarSesion(): SesionUsuario | null {
    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }

    const token = this.cargarToken();
    if (!token || this.tokenExpirado(token)) {
      this.limpiarAlmacenamiento();
      return null;
    }

    const guardada =
      localStorage.getItem(CLAVE_SESION) ??
      sessionStorage.getItem(CLAVE_SESION);
    if (!guardada) {
      return null;
    }

    try {
      const sesion = JSON.parse(guardada) as SesionUsuario;
      return sesion?.id && sesion?.rol ? sesion : null;
    } catch {
      return null;
    }
  }

  private cargarToken(): string | null {
    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }

    return (
      localStorage.getItem(CLAVE_TOKEN) ??
      sessionStorage.getItem(CLAVE_TOKEN)
    );
  }

  private limpiarAlmacenamiento(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }
    localStorage.removeItem(CLAVE_SESION);
    localStorage.removeItem(CLAVE_TOKEN);
    sessionStorage.removeItem(CLAVE_SESION);
    sessionStorage.removeItem(CLAVE_TOKEN);
  }

  private tokenExpirado(token: string): boolean {
    try {
      const partes = token.split('.');
      if (partes.length !== 3) {
        return true;
      }

      const base64 = partes[1].replace(/-/g, '+').replace(/_/g, '/');
      const relleno = '='.repeat((4 - (base64.length % 4)) % 4);
      const payload = JSON.parse(atob(base64 + relleno)) as {
        exp?: number;
      };

      return typeof payload.exp !== 'number' || payload.exp * 1000 <= Date.now();
    } catch {
      return true;
    }
  }
}
