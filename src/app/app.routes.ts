import { Routes } from '@angular/router';
import { LoginPrincipal } from './pages/login-principal/login-principal';
import { Transparencia } from './pages/transparencia/transparencia';
import { RegistroDonativos } from './pages/registro-donativos/registro-donativos';

export const routes: Routes = [
    {
        path: '',
        component: LoginPrincipal,
    },

    {
        path: 'transparencia',
        component: Transparencia,
    },

    {

        path: 'inicio',
        component: LoginPrincipal,

    },

    {

        path: 'registrar_encomienda',
        component: RegistroDonativos,

    }
    

];