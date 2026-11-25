import {
  HttpErrorResponse,
  HttpInterceptorFn,
} from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { CLAVE_SESION, CLAVE_TOKEN } from '../models/auth.model';

function leerToken(): string | null {
  if (typeof localStorage === 'undefined') {
    return null;
  }

  return (
    localStorage.getItem(CLAVE_TOKEN) ??
    sessionStorage.getItem(CLAVE_TOKEN)
  );
}

function limpiarSesionLocal(): void {
  if (typeof localStorage === 'undefined') {
    return;
  }

  localStorage.removeItem(CLAVE_TOKEN);
  localStorage.removeItem(CLAVE_SESION);
  sessionStorage.removeItem(CLAVE_TOKEN);
  sessionStorage.removeItem(CLAVE_SESION);
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = leerToken();
  const esApi = req.url.startsWith(environment.apiURL);
  const peticion =
    token && esApi
      ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
      : req;

  return next(peticion).pipe(
    catchError((error: unknown) => {
      const esLogin = req.url.includes('/api/auth/login');
      if (
        error instanceof HttpErrorResponse &&
        error.status === 401 &&
        !esLogin
      ) {
        limpiarSesionLocal();
        if (
          typeof window !== 'undefined' &&
          !window.location.pathname.endsWith('/inicio')
        ) {
          window.location.assign('/inicio');
        }
      }
      return throwError(() => error);
    }),
  );
};
