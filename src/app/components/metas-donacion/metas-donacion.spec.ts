import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MetasDonacion } from './metas-donacion';

describe('MetasDonacion', () => {
  let component: MetasDonacion;
  let fixture: ComponentFixture<MetasDonacion>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MetasDonacion],
    }).compileComponents();

    fixture = TestBed.createComponent(MetasDonacion);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
