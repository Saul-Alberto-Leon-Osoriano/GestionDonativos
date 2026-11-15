import { Routes } from '@angular/router';
import { PanelControlPrincipal } from './pages/panel-control-principal/panel-control-principal';
import { Header } from './components/header/header';
import { Footer } from './components/footer/footer';

export const routes: Routes = [
    {
        path: '',
        component: PanelControlPrincipal
    }

];