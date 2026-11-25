export type RolUsuario = 'donante' | 'administrativo';

export interface Usuario {
  id: string;
  nombre: string;
  telefono: string;
  correo: string;
  rol: RolUsuario;
  activo: boolean;
}

export interface UsuarioForm {
  nombre: string;
  telefono: string;
  correo: string;
  rol: RolUsuario;
  activo: boolean;
}

export const ROLES_USUARIO: readonly {
  valor: RolUsuario;
  etiqueta: string;
  icono: string;
}[] = [
  { valor: 'donante', etiqueta: 'Donante', icono: 'bi-heart-fill' },
  { valor: 'administrativo', etiqueta: 'Administrativo', icono: 'bi-shield-fill' },
];

export function crearUsuarioVacio(): UsuarioForm {
  return {
    nombre: '',
    telefono: '',
    correo: '',
    rol: 'donante',
    activo: true,
  };
}
