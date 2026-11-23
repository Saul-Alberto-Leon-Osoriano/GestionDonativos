import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DetallesDonacion } from './detalles-donacion';

describe('DetallesDonacion', () => {
  let component: DetallesDonacion;
  let fixture: ComponentFixture<DetallesDonacion>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DetallesDonacion],
    }).compileComponents();

    fixture = TestBed.createComponent(DetallesDonacion);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
