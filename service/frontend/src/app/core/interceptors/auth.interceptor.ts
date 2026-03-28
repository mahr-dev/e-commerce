import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

/** Login/register devuelven 401 con credenciales incorrectas: no es sesión expirada. */
function isAuthCredentialRequest(url: string): boolean {
  const path = url.split('?')[0];
  return /\/auth\/(login|register)$/.test(path);
}

/**
 * HTTP interceptor that:
 * 1. Attaches the Bearer token to every outgoing request
 * 2. On 401, solo cierra sesión si la petición iba autenticada (evita bucles con login fallido o carrito sin token)
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const token = authService.token();

  const authReq = token
    ? req.clone({
        setHeaders: { Authorization: `Bearer ${token}` },
      })
    : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        if (isAuthCredentialRequest(req.url)) {
          return throwError(() => error);
        }
        if (!authReq.headers.has('Authorization')) {
          return throwError(() => error);
        }
        authService.logout();
        router.navigate(['/auth/login']);
      }
      return throwError(() => error);
    })
  );
};
