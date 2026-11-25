import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { Transparencia } from './transparencia';

describe('Transparencia', () => {
  let component: Transparencia;
  let fixture: ComponentFixture<Transparencia>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Transparencia],
      providers: [provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(Transparencia);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
