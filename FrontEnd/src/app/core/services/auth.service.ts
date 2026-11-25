import { computed, inject, Injectable, PLATFORM_ID, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import {
  CREDENCIALES_DEMO,
  MOCK_SOLICITUDES,
  MOCK_USUARIOS,
} from '../data/mock-data';
import {
  Credenciales,
  SesionUsuario,
  SolicitudRecuperacion,
} from '../models/auth.model';
import { RolUsuario } from '../models/usuario.model';

const CLAVE_SESION = 'gestion-donativos:sesion';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly platformId = inject(PLATFORM_ID);

  readonly sesion = signal<SesionUsuario | null>(this.cargarSesion());
  readonly solicitudes = signal<SolicitudRecuperacion[]>([...MOCK_SOLICITUDES]);

  readonly estaAutenticado = computed(() => this.sesion() !== null);
  readonly esAdministrativo = computed(
    () => this.sesion()?.rol === 'administrativo',
  );
  readonly solicitudesPendientes = computed(
    () => this.solicitudes().filter((solicitud) => !solicitud.atendida).length,
  );

  async login(credenciales: Credenciales, rol: RolUsuario): Promise<boolean> {
    const demo = CREDENCIALES_DEMO[rol];
    const correo = credenciales.correo.trim().toLowerCase();
    const coincide =
      correo === demo.correo.toLowerCase() &&
      credenciales.password === demo.password;

    if (!coincide) {
      return false;
    }

    const usuario = MOCK_USUARIOS.find(
      (item) => item.id === demo.usuarioId,
    );
    if (!usuario) {
      return false;
    }

    const sesion: SesionUsuario = {
      id: usuario.id,
      nombre: usuario.nombre,
      correo: usuario.correo,
      rol: usuario.rol,
    };

    this.sesion.set(sesion);
    if (credenciales.recordar) {
      this.guardarSesion(sesion);
    } else {
      this.borrarSesion();
    }

    return true;
  }

  logout(): void {
    this.sesion.set(null);
    this.borrarSesion();
  }

  solicitarRecuperacion(correo: string): void {
    const solicitud: SolicitudRecuperacion = {
      id: `SOL-${Date.now()}`,
      correo: correo.trim().toLowerCase(),
      fecha: new Date(),
      atendida: false,
    };

    this.solicitudes.update((solicitudes) => [solicitud, ...solicitudes]);
  }

  marcarSolicitudAtendida(id: string): void {
    this.solicitudes.update((solicitudes) =>
      solicitudes.map((solicitud) =>
        solicitud.id === id ? { ...solicitud, atendida: true } : solicitud,
      ),
    );
  }

  private cargarSesion(): SesionUsuario | null {
    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }

    try {
      const guardada = localStorage.getItem(CLAVE_SESION);
      if (!guardada) {
        return null;
      }

      const sesion = JSON.parse(guardada) as SesionUsuario;
      return sesion?.id && sesion?.rol ? sesion : null;
    } catch {
      return null;
    }
  }

  private guardarSesion(sesion: SesionUsuario): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem(CLAVE_SESION, JSON.stringify(sesion));
    }
  }

  private borrarSesion(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem(CLAVE_SESION);
    }
  }
}
