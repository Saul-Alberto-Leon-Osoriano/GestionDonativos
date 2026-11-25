import { Component } from '@angular/core';
import { Header } from '../../components/header/header';
import { GestorUsuarios } from '../../components/gestor-usuarios/gestor-usuarios';
import { Footer } from '../../components/footer/footer';

@Component({
  imports: [Header, GestorUsuarios, Footer],
  selector: 'app-panel-gestor-usuarios',
  styleUrl: './panel-gestor-usuarios.css',
  templateUrl: './panel-gestor-usuarios.html',
})
export class PanelGestorUsuarios {}
