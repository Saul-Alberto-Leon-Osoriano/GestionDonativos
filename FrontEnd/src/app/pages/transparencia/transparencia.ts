import { Component } from '@angular/core';
import { Header } from '../../components/header/header';
import { Footer } from '../../components/footer/footer';
import { Resumen } from '../../components/resumen/resumen';
import { MetasDonacion } from '../../components/metas-donacion/metas-donacion';
import { LineaTiempo } from '../../components/linea-tiempo/linea-tiempo';
import { ContactarPastoral } from '../../components/contactar-pastoral/contactar-pastoral';

@Component({
  imports: [Header, Footer, Resumen, MetasDonacion, LineaTiempo, ContactarPastoral, ],
  selector: 'app-transparencia',
  styleUrl: './transparencia.css',
  templateUrl: './transparencia.html',
})
export class Transparencia {}
