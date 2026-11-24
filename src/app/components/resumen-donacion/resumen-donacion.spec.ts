import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ResumenDonacion } from './resumen-donacion';

describe('ResumenDonacion', () => {
  let component: ResumenDonacion;
  let fixture: ComponentFixture<ResumenDonacion>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResumenDonacion],
    }).compileComponents();

    fixture = TestBed.createComponent(ResumenDonacion);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
