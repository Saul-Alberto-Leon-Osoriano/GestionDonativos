import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PanelGestorUsuarios } from './panel-gestor-usuarios';

describe('PanelGestorUsuarios', () => {
  let component: PanelGestorUsuarios;
  let fixture: ComponentFixture<PanelGestorUsuarios>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PanelGestorUsuarios],
    }).compileComponents();

    fixture = TestBed.createComponent(PanelGestorUsuarios);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
