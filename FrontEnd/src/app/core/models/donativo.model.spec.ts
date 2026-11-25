import { calcularPesoNeto, calcularResumenDonativo, crearArticuloVacio, crearDonativoVacio, fechaUTC } from './donativo.model';

function enDias(dias: number): Date {
  const hoy = new Date();
  return fechaUTC(hoy.getFullYear(), hoy.getMonth(), hoy.getDate() + dias);
}

describe('modelo de donativo', () => {
  it('calcula el peso neto multiplicando cantidad por peso unitario', () => {
    const articulos = [
      { ...crearArticuloVacio(), cantidad: 4, pesoUnitarioKg: 2.5 },
      { ...crearArticuloVacio(), cantidad: 2, pesoUnitarioKg: 0.4 },
    ];

    expect(calcularPesoNeto(articulos)).toBe(10.8);
  });

  it('resume unidades, peso y artículos por vencer', () => {
    const draft = crearDonativoVacio();
    draft.articulos = [
      {
        ...crearArticuloVacio(),
        cantidad: 3,
        pesoUnitarioKg: 2,
        fechaVencimiento: enDias(10),
      },
    ];

    const resumen = calcularResumenDonativo(draft);

    expect(resumen.totalArticulos).toBe(1);
    expect(resumen.totalUnidades).toBe(3);
    expect(resumen.pesoNetoKg).toBe(6);
    expect(resumen.articulosPorVencer).toBe(1);
  });
});
