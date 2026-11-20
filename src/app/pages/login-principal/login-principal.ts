import { Component } from '@angular/core';
import { Footer } from '../../components/footer/footer';
import { Header } from '../../components/header/header';
import { Login } from '../../components/login/login';

@Component({
  imports: [Footer, Header, Login],
  selector: 'app-login-principal',
  styleUrl: './login-principal.css',
  templateUrl: './login-principal.html',
})
export class LoginPrincipal {}
