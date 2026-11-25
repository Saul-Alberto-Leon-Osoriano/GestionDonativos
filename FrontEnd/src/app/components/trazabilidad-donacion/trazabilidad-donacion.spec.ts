import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TrazabilidadDonacion } from './trazabilidad-donacion';

describe('TrazabilidadDonacion', () => {
  let component: TrazabilidadDonacion;
  let fixture: ComponentFixture<TrazabilidadDonacion>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TrazabilidadDonacion],
    }).compileComponents();

    fixture = TestBed.createComponent(TrazabilidadDonacion);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
