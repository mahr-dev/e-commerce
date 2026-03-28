import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  CheckoutResponse,
  CheckoutRequest,
  Order,
  ShippingAddress,
} from '../../shared/models/order.model';

export interface StripeStatus {
  enabled: boolean;
  publishable_key: string;
}

export interface StripePaymentIntentResponse {
  client_secret: string;
  order_id: string;
}

export interface StripeConfirmResponse {
  order: Order;
  payment_intent_id: string;
}

@Injectable({ providedIn: 'root' })
export class PaymentService {
  private readonly checkoutUrl = `${environment.apiUrl}/checkout`;
  private readonly paymentBase = `${environment.apiUrl}/payment`;

  constructor(private http: HttpClient) {}

  /**
   * Submit checkout: dirección manual o guardada; tarjeta nueva o guardada (mock).
   */
  checkout(body: CheckoutRequest): Observable<CheckoutResponse> {
    return this.http.post<CheckoutResponse>(this.checkoutUrl, body);
  }

  getStripeStatus(): Observable<StripeStatus> {
    return this.http.get<StripeStatus>(`${this.paymentBase}/stripe/status`);
  }

  createStripePaymentIntent(body: {
    shipping_address?: ShippingAddress;
    saved_address_id?: string;
  }): Observable<StripePaymentIntentResponse> {
    return this.http.post<StripePaymentIntentResponse>(
      `${this.paymentBase}/stripe/payment-intent`,
      body
    );
  }

  confirmStripePayment(payment_intent_id: string): Observable<StripeConfirmResponse> {
    return this.http.post<StripeConfirmResponse>(
      `${this.paymentBase}/stripe/confirm`,
      { payment_intent_id }
    );
  }
}
