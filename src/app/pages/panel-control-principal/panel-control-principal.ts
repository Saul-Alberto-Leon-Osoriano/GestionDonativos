import { Component } from '@angular/core';
import { Header } from '../../components/header/header';
import { Footer } from '../../components/footer/footer';
import { TargetasSuperiores } from '../../components/targetas-superiores/targetas-superiores';
import { AlertaCaducidad } from '../../components/alerta-caducidad/alerta-caducidad';
import { GestionLotes } from '../../components/gestion-lotes/gestion-lotes';

@Component({
  imports: [Header, Footer, TargetasSuperiores, AlertaCaducidad, GestionLotes],
  selector: 'app-panel-control-principal',
  styleUrl: './panel-control-principal.css',
  templateUrl: './panel-control-principal.html',
})
export class PanelControlPrincipal {}
