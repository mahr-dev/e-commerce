import { ShippingAddress } from './order.model';

export interface SavedAddress extends ShippingAddress {
  id: string;
  label: string;
  is_default: boolean;
}

export interface SavedPaymentMethod {
  id: string;
  brand: string;
  last4: string;
  expiry: string;
  label?: string | null;
  is_default: boolean;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  phone?: string | null;
  addresses: SavedAddress[];
  payment_methods: SavedPaymentMethod[];
}

export interface ProfilePatch {
  name?: string;
  phone?: string | null;
}

export interface PaymentMethodCreate {
  brand: string;
  last4: string;
  expiry: string;
  label?: string | null;
  is_default?: boolean;
}
