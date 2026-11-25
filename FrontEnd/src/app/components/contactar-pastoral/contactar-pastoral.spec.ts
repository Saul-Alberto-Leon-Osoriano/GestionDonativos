import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ContactarPastoral } from './contactar-pastoral';

describe('ContactarPastoral', () => {
  let component: ContactarPastoral;
  let fixture: ComponentFixture<ContactarPastoral>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContactarPastoral],
    }).compileComponents();

    fixture = TestBed.createComponent(ContactarPastoral);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
