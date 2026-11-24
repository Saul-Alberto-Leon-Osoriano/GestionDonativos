import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RegistroDonativos } from './registro-donativos';

describe('RegistroDonativos', () => {
  let component: RegistroDonativos;
  let fixture: ComponentFixture<RegistroDonativos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegistroDonativos],
    }).compileComponents();

    fixture = TestBed.createComponent(RegistroDonativos);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
