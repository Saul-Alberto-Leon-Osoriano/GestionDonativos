import { RolUsuario } from './usuario.model';

export interface Credenciales {
  correo: string;
  password: string;
  recordar: boolean;
}

export interface SesionUsuario {
  id: string;
  nombre: string;
  correo: string;
  rol: RolUsuario;
}

export interface RecuperacionForm {
  correo: string;
}

export interface SolicitudRecuperacion {
  id: string;
  correo: string;
  fecha: Date;
  atendida: boolean;
}
