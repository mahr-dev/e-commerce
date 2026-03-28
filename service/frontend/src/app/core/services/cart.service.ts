import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Cart, AddToCartRequest } from '../../shared/models/cart.model';

@Injectable({ providedIn: 'root' })
export class CartService {
  private readonly baseUrl = `${environment.apiUrl}/cart`;

  /** Reactive cart state */
  private readonly _cart = signal<Cart | null>(null);
  readonly cart = this._cart.asReadonly();

  /** Reactive cart item count (for toolbar badge) */
  readonly itemCount = computed(() => {
    const items = this._cart()?.items ?? [];
    return items.reduce((sum, item) => sum + item.quantity, 0);
  });

  /** Reactive cart total */
  readonly total = computed(() => this._cart()?.total ?? 0);

  constructor(private http: HttpClient) {}

  /** Load cart from the API and update local state */
  loadCart(): Observable<Cart> {
    return this.http
      .get<Cart>(this.baseUrl)
      .pipe(tap((cart) => this._cart.set(cart)));
  }

  addItem(request: AddToCartRequest): Observable<Cart> {
    return this.http
      .post<Cart>(this.baseUrl, request)
      .pipe(tap((cart) => this._cart.set(cart)));
  }

  updateQuantity(productId: string, quantity: number): Observable<Cart> {
    return this.http
      .put<Cart>(`${this.baseUrl}/${productId}`, { quantity })
      .pipe(tap((cart) => this._cart.set(cart)));
  }

  removeItem(productId: string): Observable<Cart> {
    return this.http
      .delete<Cart>(`${this.baseUrl}/${productId}`)
      .pipe(tap((cart) => this._cart.set(cart)));
  }

  clearCart(): Observable<{ message: string }> {
    return this.http
      .delete<{ message: string }>(this.baseUrl)
      .pipe(tap(() => this._cart.set(null)));
  }

  /** Reset cart signal without an API call (used after successful checkout) */
  resetLocal(): void {
    this._cart.set(null);
  }
}
