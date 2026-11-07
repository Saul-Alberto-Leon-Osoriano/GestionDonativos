import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PanelControlPrincipal } from './panel-control-principal';

describe('PanelControlPrincipal', () => {
  let component: PanelControlPrincipal;
  let fixture: ComponentFixture<PanelControlPrincipal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PanelControlPrincipal],
    }).compileComponents();

    fixture = TestBed.createComponent(PanelControlPrincipal);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
