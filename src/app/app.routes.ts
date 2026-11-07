import { Routes } from '@angular/router';
import { PanelControlPrincipal } from './pages/panel-control-principal/panel-control-principal';
import { Header } from './shared/header/header';
import { Footer } from './shared/footer/footer';

export const routes: Routes = [
    {
        path: '',
        component: PanelControlPrincipal
    }

];