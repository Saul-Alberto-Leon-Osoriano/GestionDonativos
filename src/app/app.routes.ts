import { Routes } from '@angular/router';
import { PanelControlPrincipal } from './pages/panel-control-principal/panel-control-principal';
import { Header } from './components/header/header';
import { Footer } from './components/footer/footer';
import { Transparencia } from './pages/transparencia/transparencia';

export const routes: Routes = [
    {
        path: '',
        component: Transparencia
    }

];