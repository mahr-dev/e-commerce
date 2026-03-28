import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  User,
} from '../../shared/models/user.model';

const TOKEN_KEY = 'ecommerce_token';
const USER_KEY = 'ecommerce_user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly _token = signal<string | null>(
    localStorage.getItem(TOKEN_KEY)
  );
  private readonly _user = signal<User | null>(
    this._parseStoredUser()
  );

  /** Reactive: whether the user is currently authenticated */
  readonly isAuthenticated = computed(() => !!this._token());
  /** Reactive: current logged-in user */
  readonly currentUser = this._user.asReadonly();
  /** Reactive: current token */
  readonly token = this._token.asReadonly();

  constructor(private http: HttpClient, private router: Router) {}

  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${environment.apiUrl}/auth/login`, credentials)
      .pipe(tap((res) => this._storeSession(res)));
  }

  register(data: RegisterRequest): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${environment.apiUrl}/auth/register`, data)
      .pipe(tap((res) => this._storeSession(res)));
  }

  /** Actualiza datos locales tras guardar perfil (nombre, teléfono). */
  patchLocalUser(partial: Partial<User>): void {
    const cur = this._user();
    if (!cur) return;
    const next = { ...cur, ...partial };
    localStorage.setItem(USER_KEY, JSON.stringify(next));
    this._user.set(next);
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    this._token.set(null);
    this._user.set(null);
    this.router.navigate(['/auth/login']);
  }

  /** Store JWT and user data in localStorage and update signals */
  private _storeSession(res: AuthResponse): void {
    localStorage.setItem(TOKEN_KEY, res.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(res.user));
    this._token.set(res.access_token);
    this._user.set(res.user);
  }

  private _parseStoredUser(): User | null {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }
}
