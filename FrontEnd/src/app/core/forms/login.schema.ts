import { email, minLength, required, schema } from '@angular/forms/signals';
import { Credenciales, RecuperacionForm } from '../models/auth.model';

export const loginSchema = schema<Credenciales>((path) => {
  required(path.correo, {
    message: 'Ingresa tu correo electrónico.',
  });
  email(path.correo, {
    message: 'Ingresa un correo electrónico válido.',
  });
  required(path.password, {
    message: 'Ingresa tu contraseña.',
  });
  minLength(path.password, 6, {
    message: 'La contraseña debe tener al menos 6 caracteres.',
  });
});

export const recuperacionSchema = schema<RecuperacionForm>((path) => {
  required(path.correo, {
    message: 'Ingresa el correo con el que te registraste.',
  });
  email(path.correo, {
    message: 'Ingresa un correo electrónico válido.',
  });
});
