import { Component } from '@angular/core';
import { Header } from '../../components/header/header';
import { Footer } from '../../components/footer/footer';
import { TargetasSuperiores } from '../../components/targetas-superiores/targetas-superiores';

@Component({
  imports: [Header, Footer, TargetasSuperiores],
  selector: 'app-panel-control-principal',
  styleUrl: './panel-control-principal.css',
  templateUrl: './panel-control-principal.html',
})
export class PanelControlPrincipal {}
