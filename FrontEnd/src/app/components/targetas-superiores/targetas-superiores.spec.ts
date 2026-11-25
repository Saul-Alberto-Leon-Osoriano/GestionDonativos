import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { TargetasSuperiores } from './targetas-superiores';

describe('TargetasSuperiores', () => {
  let component: TargetasSuperiores;
  let fixture: ComponentFixture<TargetasSuperiores>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TargetasSuperiores],
      providers: [provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(TargetasSuperiores);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
