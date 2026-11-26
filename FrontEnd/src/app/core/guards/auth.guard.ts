import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  return auth.estaAutenticado() ? true : router.createUrlTree(['/inicio']);
};

export const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.estaAutenticado()) {
    return router.createUrlTree(['/inicio']);
  }

  return auth.esAdministrativo()
    ? true
    : router.createUrlTree(['/transparencia']);
};
