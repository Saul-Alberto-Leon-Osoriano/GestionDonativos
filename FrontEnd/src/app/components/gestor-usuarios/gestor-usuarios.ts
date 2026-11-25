import { Component, inject, signal } from '@angular/core';
import { FormField, form, submit } from '@angular/forms/signals';
import { UsuarioService } from '../../core/services/usuario.service';
import {
  crearUsuarioVacio,
  ROLES_USUARIO,
  Usuario,
  UsuarioForm,
} from '../../core/models/usuario.model';
import { usuarioSchema } from '../../core/forms/usuario.schema';
import { FormError } from '../../shared/form-error/form-error';
import { descargarArchivo } from '../../shared/download';
import { mensajeErrorApi } from '../../core/utils/api.utils';

@Component({
  imports: [FormField, FormError],
  selector: 'app-gestor-usuarios',
  styleUrl: './gestor-usuarios.css',
  templateUrl: './gestor-usuarios.html',
})
export class GestorUsuarios {
  readonly usuariosService = inject(UsuarioService);
  readonly roles = ROLES_USUARIO;

  readonly modelo = signal<UsuarioForm>(crearUsuarioVacio());
  readonly formulario = form(this.modelo, usuarioSchema);

  readonly mostrarModal = signal(false);
  readonly editandoId = signal<string | null>(null);
  readonly mensaje = signal<string | null>(null);
  readonly error = signal<string | null>(null);

  readonly usuarios = this.usuariosService.usuariosFiltrados;
  readonly totales = this.usuariosService.totales;

  abrirNuevo(): void {
    this.editandoId.set(null);
    this.modelo.set(crearUsuarioVacio());
    this.formulario().reset(crearUsuarioVacio());
    this.mensaje.set(null);
    this.error.set(null);
    this.mostrarModal.set(true);
  }

  abrirEditar(usuario: Usuario): void {
    const datos: UsuarioForm = {
      nombre: usuario.nombre,
      telefono: usuario.telefono,
      correo: usuario.correo,
      password: '',
      rol: usuario.rol,
      activo: usuario.activo,
    };

    this.editandoId.set(usuario.id);
    this.modelo.set(datos);
    this.formulario().reset(datos);
    this.mensaje.set(null);
    this.error.set(null);
    this.mostrarModal.set(true);
  }

  cerrarModal(): void {
    this.mostrarModal.set(false);
  }

  buscar(evento: Event): void {
    this.usuariosService.buscar((evento.target as HTMLInputElement).value);
  }

  async guardar(evento: Event): Promise<void> {
    evento.preventDefault();
    this.error.set(null);

    await submit(this.formulario, async () => {
      const datos = this.modelo();
      const id = this.editandoId();

      if (!id && !datos.password.trim()) {
        this.error.set(
          'Ingresa una contraseña temporal para el nuevo usuario.',
        );
        return;
      }

      try {
        if (id) {
          const actualizado = await this.usuariosService.actualizar(id, datos);
          this.mensaje.set(
            `Usuario ${actualizado?.id ?? id} actualizado correctamente.`,
          );
        } else {
          const creado = await this.usuariosService.crear(datos);
          this.mensaje.set(`Usuario ${creado.id} creado correctamente.`);
        }

        this.mostrarModal.set(false);
      } catch (error) {
        this.error.set(mensajeErrorApi(error));
      }
    });
  }

  async eliminar(usuario: Usuario): Promise<void> {
    if (
      typeof window !== 'undefined' &&
      !window.confirm(`¿Eliminar a ${usuario.nombre}?`)
    ) {
      return;
    }

    this.error.set(null);

    try {
      await this.usuariosService.eliminar(usuario.id);
      this.mensaje.set(`Usuario ${usuario.id} eliminado.`);
    } catch (error) {
      this.error.set(mensajeErrorApi(error));
    }
  }

  exportar(): void {
    descargarArchivo(
      `usuarios-${new Date().toISOString().slice(0, 10)}.csv`,
      this.usuariosService.exportarCsv(),
    );
  }
}
