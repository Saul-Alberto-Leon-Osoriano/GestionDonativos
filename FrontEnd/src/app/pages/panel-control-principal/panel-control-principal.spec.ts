import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { PanelControlPrincipal } from './panel-control-principal';

describe('PanelControlPrincipal', () => {
  let component: PanelControlPrincipal;
  let fixture: ComponentFixture<PanelControlPrincipal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PanelControlPrincipal],
      providers: [provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(PanelControlPrincipal);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
