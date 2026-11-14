import { Component } from '@angular/core';
import { Header } from '../../shared/header/header';
import { Footer } from '../../shared/footer/footer';
import { Login } from './login/login';

@Component({
  imports: [Header, Footer, Login],
  selector: 'app-panel-control-principal',
  styleUrl: './panel-control-principal.css',
  templateUrl: './panel-control-principal.html',
})
export class PanelControlPrincipal {}
