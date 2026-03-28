export interface OrderItem {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
}

export interface ShippingAddress {
  full_name: string;
  line1: string;
  line2?: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface TrackingEvent {
  at: string;
  description: string;
  location?: string | null;
}

export interface Order {
  id: string;
  user_id: string;
  items: OrderItem[];
  total: number;
  status: 'pending' | 'paid' | 'failed' | 'shipped' | 'cancelled';
  payment_id?: string;
  created_at: string;
  shipping_address?: ShippingAddress | Record<string, unknown>;
  tracking_number?: string | null;
  carrier?: string | null;
  tracking_events?: TrackingEvent[];
}

export interface CheckoutRequest {
  shipping_address?: ShippingAddress;
  saved_address_id?: string;
  card_number?: string;
  card_holder?: string;
  expiry?: string;
  cvv?: string;
  saved_payment_method_id?: string;
}

/** @deprecated legacy mock-only shape; use CheckoutRequest */
export interface PaymentRequest {
  order_id: string;
  amount: number;
  card_number: string;
  card_holder: string;
  expiry: string;
  cvv: string;
}

export interface PaymentResponse {
  success: boolean;
  transaction_id?: string;
  status: 'success' | 'failure' | 'pending';
  message: string;
}

export interface CheckoutResponse {
  order: Order;
  payment: PaymentResponse;
}
