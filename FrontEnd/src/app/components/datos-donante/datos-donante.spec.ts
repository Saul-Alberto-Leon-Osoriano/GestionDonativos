import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DatosDonante } from './datos-donante';

describe('DatosDonante', () => {
  let component: DatosDonante;
  let fixture: ComponentFixture<DatosDonante>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DatosDonante],
    }).compileComponents();

    fixture = TestBed.createComponent(DatosDonante);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
