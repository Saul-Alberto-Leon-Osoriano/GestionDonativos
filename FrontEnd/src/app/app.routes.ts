import { Routes } from '@angular/router';
import { adminGuard } from './core/guards/auth.guard';
import { LoginPrincipal } from './pages/login-principal/login-principal';
import { PanelControlPrincipal } from './pages/panel-control-principal/panel-control-principal';
import { PanelGestorUsuarios } from './pages/panel-gestor-usuarios/panel-gestor-usuarios';
import { RegistroDonativos } from './pages/registro-donativos/registro-donativos';
import { Transparencia } from './pages/transparencia/transparencia';

export const routes: Routes = [
  {
    path: '',
    component: LoginPrincipal,
  },
  {
    path: 'inicio',
    component: LoginPrincipal,
  },
  {
    path: 'transparencia',
    component: Transparencia,
  },
  {
    path: 'registrar_encomienda',
    component: RegistroDonativos,
    canActivate: [adminGuard],
  },
  {
    path: 'panel-control',
    component: PanelControlPrincipal,
    canActivate: [adminGuard],
  },
  {
    path: 'gestor-usuarios',
    component: PanelGestorUsuarios,
    canActivate: [adminGuard],
  },
  {
    path: '**',
    redirectTo: 'inicio',
  },
];
