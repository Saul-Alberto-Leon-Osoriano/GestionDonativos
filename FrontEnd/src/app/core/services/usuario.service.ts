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
import { Usuario, UsuarioForm } from '../models/usuario.model';
import { mensajeErrorApi } from '../utils/api.utils';

@Injectable({ providedIn: 'root' })
export class UsuarioService {
  private readonly http = inject(HttpClient);
  private readonly esNavegador = isPlatformBrowser(inject(PLATFORM_ID));
  private readonly apiURL = environment.apiURL;

  private readonly usuariosState = signal<Usuario[]>([]);
  private readonly cargandoState = signal(false);
  private readonly errorState = signal<string | null>(null);

  readonly usuarios = this.usuariosState.asReadonly();
  readonly cargando = this.cargandoState.asReadonly();
  readonly error = this.errorState.asReadonly();
  readonly busqueda = signal('');

  readonly usuariosFiltrados = computed(() => {
    const termino = this.busqueda().trim().toLowerCase();
    if (!termino) {
      return this.usuariosState();
    }

    return this.usuariosState().filter((usuario) =>
      [usuario.id, usuario.nombre, usuario.telefono, usuario.correo, usuario.rol]
        .join(' ')
        .toLowerCase()
        .includes(termino),
    );
  });

  readonly totales = computed(() => {
    const usuarios = this.usuariosState();
    return {
      total: usuarios.length,
      administrativos: usuarios.filter(
        (usuario) => usuario.rol === 'administrativo',
      ).length,
      donantes: usuarios.filter((usuario) => usuario.rol === 'donante').length,
      activos: usuarios.filter((usuario) => usuario.activo).length,
    };
  });

  constructor() {
    void this.recargar();
  }

  async recargar(): Promise<void> {
    if (!this.esNavegador) {
      return;
    }

    this.cargandoState.set(true);
    this.errorState.set(null);

    try {
      const usuarios = await firstValueFrom(
        this.http.get<Usuario[]>(`${this.apiURL}/api/usuarios`),
      );
      this.usuariosState.set(usuarios);
    } catch (error) {
      this.errorState.set(mensajeErrorApi(error));
    } finally {
      this.cargandoState.set(false);
    }
  }

  obtenerPorId(id: string): Usuario | undefined {
    return this.usuariosState().find((usuario) => usuario.id === id);
  }

  buscar(termino: string): void {
    this.busqueda.set(termino);
  }

  async crear(datos: UsuarioForm): Promise<Usuario> {
    const usuario = await firstValueFrom(
      this.http.post<Usuario>(`${this.apiURL}/api/usuarios`, datos),
    );

    this.usuariosState.update((usuarios) => [usuario, ...usuarios]);
    return usuario;
  }

  async actualizar(
    id: string,
    datos: UsuarioForm,
  ): Promise<Usuario | undefined> {
    const { password, ...resto } = datos;
    const payload = password.trim() ? { ...resto, password } : resto;
    const actualizado = await firstValueFrom(
      this.http.put<Usuario>(`${this.apiURL}/api/usuarios/${id}`, payload),
    );

    this.usuariosState.update((usuarios) =>
      usuarios.map((usuario) =>
        usuario.id === id ? actualizado : usuario,
      ),
    );

    return actualizado;
  }

  async eliminar(id: string): Promise<void> {
    await firstValueFrom(
      this.http.delete<{ detail: string }>(
        `${this.apiURL}/api/usuarios/${id}`,
      ),
    );

    this.usuariosState.update((usuarios) =>
      usuarios.filter((usuario) => usuario.id !== id),
    );
  }

  exportarCsv(): string {
    const encabezados = ['ID', 'Nombre', 'Telefono', 'Correo', 'Rol', 'Activo'];
    const filas = this.usuariosState().map((usuario) => [
      usuario.id,
      usuario.nombre,
      usuario.telefono,
      usuario.correo,
      usuario.rol,
      usuario.activo ? 'Si' : 'No',
    ]);

    return [encabezados, ...filas]
      .map((fila) =>
        fila
          .map((celda) => `"${String(celda).replaceAll('"', '""')}"`)
          .join(','),
      )
      .join('\n');
  }
}
