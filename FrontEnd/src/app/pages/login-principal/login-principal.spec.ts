import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { LoginPrincipal } from './login-principal';

describe('LoginPrincipal', () => {
  let component: LoginPrincipal;
  let fixture: ComponentFixture<LoginPrincipal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginPrincipal],
      providers: [provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(LoginPrincipal);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
