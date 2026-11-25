import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AlertaCaducidad } from './alerta-caducidad';

describe('AlertaCaducidad', () => {
  let component: AlertaCaducidad;
  let fixture: ComponentFixture<AlertaCaducidad>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlertaCaducidad],
    }).compileComponents();

    fixture = TestBed.createComponent(AlertaCaducidad);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
