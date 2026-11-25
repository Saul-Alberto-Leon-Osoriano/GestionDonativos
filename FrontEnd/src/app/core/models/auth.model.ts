import { RolUsuario } from './usuario.model';

export const CLAVE_TOKEN = 'gestion-donativos:token';
export const CLAVE_SESION = 'gestion-donativos:sesion';

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

export interface RespuestaLogin {
  accessToken: string;
  tokenType: string;
  expiraEn: number;
  usuario: SesionUsuario;
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
