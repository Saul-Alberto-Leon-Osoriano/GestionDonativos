import { Component } from '@angular/core';
import { Header } from '../../components/header/header';
import { Footer } from '../../components/footer/footer';
import { DatosDonante } from '../../components/datos-donante/datos-donante';
import { DetallesDonacion } from '../../components/detalles-donacion/detalles-donacion';
import { ResumenDonacion } from '../../components/resumen-donacion/resumen-donacion';
import { TrazabilidadDonacion } from '../../components/trazabilidad-donacion/trazabilidad-donacion';
import { TituloDonacion } from '../../components/titulo-donacion/titulo-donacion';

@Component({
  imports: [Header, Footer, TituloDonacion, DatosDonante, DetallesDonacion, ResumenDonacion, TrazabilidadDonacion],
  selector: 'app-registro-donativos',
  styleUrl: './registro-donativos.css',
  templateUrl: './registro-donativos.html',
})
export class RegistroDonativos {}
