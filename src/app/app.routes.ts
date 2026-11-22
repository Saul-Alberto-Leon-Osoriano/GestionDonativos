import { Routes } from '@angular/router';
import { LoginPrincipal } from './pages/login-principal/login-principal';
import { Transparencia } from './pages/transparencia/transparencia';

export const routes: Routes = [
    {
        path: '',
        component: LoginPrincipal,
    },

    {
        path: 'transparencia',
        component: Transparencia,
    },

];