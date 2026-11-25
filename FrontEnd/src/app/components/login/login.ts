import { Component, inject, signal } from '@angular/core';
import { FormField, form, submit } from '@angular/forms/signals';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { Credenciales, RecuperacionForm } from '../../core/models/auth.model';
import { RolUsuario } from '../../core/models/usuario.model';
import { loginSchema, recuperacionSchema } from '../../core/forms/login.schema';
import { FormError } from '../../shared/form-error/form-error';

@Component({
  imports: [FormField, FormError, RouterLink],
  selector: 'app-login',
  styleUrl: './login.css',
  templateUrl: './login.html',
})
export class Login {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly modelo = signal<Credenciales>({
    correo: '',
    password: '',
    recordar: false,
  });
  readonly formulario = form(this.modelo, loginSchema);

  readonly tipoAcceso = signal<RolUsuario>('administrativo');
  readonly errorLogin = signal<string | null>(null);

  readonly mostrarRecuperacion = signal(false);
  readonly recuperacionEnviada = signal(false);
  readonly recuperacionModelo = signal<RecuperacionForm>({ correo: '' });
  readonly recuperacionFormulario = form(
    this.recuperacionModelo,
    recuperacionSchema,
  );

  seleccionarTipo(rol: RolUsuario): void {
    this.tipoAcceso.set(rol);
    this.errorLogin.set(null);
  }

  ingresar(evento: Event): void {
    evento.preventDefault();
    this.errorLogin.set(null);

    void submit(this.formulario, async () => {
      const accesoCorrecto = await this.auth.login(this.modelo());

      if (!accesoCorrecto) {
        this.errorLogin.set(
          this.auth.error() ?? 'Correo o contraseña incorrectos.',
        );
        return;
      }

      const destino = this.auth.esAdministrativo()
        ? '/panel-control'
        : '/transparencia';
      await this.router.navigateByUrl(destino);
    });
  }

  abrirRecuperacion(): void {
    this.recuperacionModelo.set({ correo: this.modelo().correo });
    this.recuperacionFormulario().reset();
    this.recuperacionEnviada.set(false);
    this.mostrarRecuperacion.set(true);
  }

  cerrarRecuperacion(): void {
    this.mostrarRecuperacion.set(false);
  }

  solicitarRecuperacion(evento: Event): void {
    evento.preventDefault();

    void submit(this.recuperacionFormulario, async () => {
      const enviada = await this.auth.solicitarRecuperacion(
        this.recuperacionModelo().correo,
      );
      if (enviada) {
        this.recuperacionEnviada.set(true);
      } else {
        this.errorLogin.set(
          this.auth.error() ?? 'No se pudo registrar la solicitud.',
        );
      }
    });
  }
}
