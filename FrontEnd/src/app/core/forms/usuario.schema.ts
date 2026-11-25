import { email, minLength, pattern, required, schema } from '@angular/forms/signals';
import { UsuarioForm } from '../models/usuario.model';

export const usuarioSchema = schema<UsuarioForm>((path) => {
  required(path.nombre, {
    message: 'Ingresa el nombre completo o la razón social.',
  });
  minLength(path.nombre, 3, {
    message: 'El nombre debe tener al menos 3 caracteres.',
  });
  required(path.telefono, {
    message: 'Ingresa un teléfono de contacto.',
  });
  pattern(path.telefono, /^[+0-9 ()-]{6,}$/, {
    message: 'Usa solo números, espacios, paréntesis, guiones o el prefijo +.',
  });
  required(path.correo, {
    message: 'Ingresa el correo electrónico.',
  });
  email(path.correo, {
    message: 'Ingresa un correo electrónico válido.',
  });
  required(path.rol, {
    message: 'Selecciona el tipo de usuario.',
  });
});
