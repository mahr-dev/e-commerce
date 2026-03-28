import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  UserProfile,
  ProfilePatch,
  SavedAddress,
  SavedPaymentMethod,
  PaymentMethodCreate,
} from '../../shared/models/account.model';

@Injectable({ providedIn: 'root' })
export class AccountService {
  private readonly base = `${environment.apiUrl}/account`;

  constructor(private http: HttpClient) {}

  getProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>(`${this.base}/me`);
  }

  updateProfile(body: ProfilePatch): Observable<UserProfile> {
    return this.http.patch<UserProfile>(`${this.base}/me`, body);
  }

  addAddress(
    body: Omit<SavedAddress, 'id'>
  ): Observable<SavedAddress> {
    return this.http.post<SavedAddress>(`${this.base}/addresses`, body);
  }

  updateAddress(
    id: string,
    body: Omit<SavedAddress, 'id'>
  ): Observable<SavedAddress> {
    return this.http.patch<SavedAddress>(
      `${this.base}/addresses/${id}`,
      body
    );
  }

  deleteAddress(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/addresses/${id}`);
  }

  addPaymentMethod(body: PaymentMethodCreate): Observable<SavedPaymentMethod> {
    return this.http.post<SavedPaymentMethod>(
      `${this.base}/payment-methods`,
      body
    );
  }

  deletePaymentMethod(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/payment-methods/${id}`);
  }

  setDefaultPaymentMethod(id: string): Observable<UserProfile> {
    return this.http.post<UserProfile>(
      `${this.base}/payment-methods/${id}/default`,
      {}
    );
  }
}
