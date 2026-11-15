import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { PanelControlPrincipal } from './pages/panel-control-principal/panel-control-principal';
import { Header } from './components/header/header';
import { Footer } from './components/footer/footer';

@Component({
  imports: [RouterOutlet, PanelControlPrincipal, Header, Footer],
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App {
  protected readonly title = signal('GestionDonativos');
}
