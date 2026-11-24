import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TituloDonacion } from './titulo-donacion';

describe('TituloDonacion', () => {
  let component: TituloDonacion;
  let fixture: ComponentFixture<TituloDonacion>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TituloDonacion],
    }).compileComponents();

    fixture = TestBed.createComponent(TituloDonacion);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
