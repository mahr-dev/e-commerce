import {
  Component,
  OnInit,
  OnDestroy,
  signal,
  ElementRef,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
  AbstractControl,
  ValidationErrors,
} from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatRadioModule } from '@angular/material/radio';
import { loadStripe, Stripe, StripeCardElement } from '@stripe/stripe-js';
import { CartService } from '../../../core/services/cart.service';
import { PaymentService } from '../../../core/services/payment.service';
import { AccountService } from '../../../core/services/account.service';
import { CheckoutRequest, CheckoutResponse } from '../../../shared/models/order.model';
import { UserProfile } from '../../../shared/models/account.model';
import {
  detectCardBrand,
  expectedCardLength,
  formatCardDisplay,
  cardBrandLabel,
  luhnCheck,
  CardBrand,
} from '../../../shared/utils/card-brand';

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    MatSnackBarModule,
    MatSelectModule,
    MatButtonToggleModule,
    MatRadioModule,
  ],
  templateUrl: './checkout.component.html',
  styleUrl: './checkout.component.scss',
})
export class CheckoutComponent implements OnInit, OnDestroy {
  @ViewChild('stripeMount') stripeMount?: ElementRef<HTMLDivElement>;

  readonly addressForm: FormGroup;
  readonly paymentForm: FormGroup;
  readonly loading = signal(false);
  readonly checkoutResult = signal<CheckoutResponse | null>(null);

  readonly cart = this.cartService.cart;
  readonly cartTotal = this.cartService.total;
  readonly itemCount = this.cartService.itemCount;

  readonly profile = signal<UserProfile | null>(null);
  readonly addressSource = signal<'saved' | 'new'>('new');
  readonly cardSource = signal<'saved' | 'new'>('new');
  readonly selectedAddressId = signal<string | null>(null);
  readonly selectedPaymentMethodId = signal<string | null>(null);

  readonly cardBrand = signal<CardBrand>('unknown');
  readonly stripeEnabled = signal(false);
  readonly stripePublishableKey = signal('');
  readonly paymentMode = signal<'mock' | 'stripe'>('mock');

  private stripe: Stripe | null = null;
  private cardElement: StripeCardElement | null = null;

  constructor(
    private fb: FormBuilder,
    private cartService: CartService,
    private paymentService: PaymentService,
    private accountService: AccountService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {
    this.addressForm = this.fb.group({
      full_name: ['', [Validators.required, Validators.minLength(2)]],
      line1: ['', [Validators.required, Validators.minLength(3)]],
      line2: [''],
      city: ['', Validators.required],
      state: ['', Validators.required],
      postal_code: ['', Validators.required],
      country: ['ES', Validators.required],
      phone: [''],
      latitude: [''],
      longitude: [''],
    });

    this.paymentForm = this.fb.group({
      card_holder: ['', [Validators.required, Validators.minLength(3)]],
      card_number: ['', [Validators.required, this.cardNumberValidator]],
      expiry: ['', [Validators.required, Validators.pattern(/^\d{2}\/\d{2}$/)]],
      cvv: ['', [Validators.required, Validators.pattern(/^\d{3,4}$/)]],
    });
  }

  ngOnInit(): void {
    this.paymentService.getStripeStatus().subscribe({
      next: (s) => {
        this.stripeEnabled.set(s.enabled);
        this.stripePublishableKey.set(s.publishable_key || '');
      },
      error: () => {
        this.stripeEnabled.set(false);
      },
    });

    this.accountService.getProfile().subscribe({
      next: (p) => {
        this.profile.set(p);
        if (p.addresses?.length) {
          this.addressSource.set('saved');
          const def =
            p.addresses.find((a) => a.is_default) ?? p.addresses[0];
          this.selectedAddressId.set(def.id);
          this.addressForm.disable({ emitEvent: false });
        } else {
          this.addressSource.set('new');
        }
        if (p.payment_methods?.length) {
          this.cardSource.set('saved');
          const pm =
            p.payment_methods.find((x) => x.is_default) ??
            p.payment_methods[0];
          this.selectedPaymentMethodId.set(pm.id);
        } else {
          this.cardSource.set('new');
        }
        this.syncPaymentValidators();
      },
      error: () => {
        this.syncPaymentValidators();
      },
    });

    this.cartService.loadCart().subscribe({
      next: () => {
        if (this.itemCount() === 0) {
          this.router.navigate(['/cart']);
        }
      },
    });
  }

  ngOnDestroy(): void {
    this.cardElement?.destroy();
    this.cardElement = null;
    this.stripe = null;
  }

  cardBrandLabel(): string {
    return cardBrandLabel(this.cardBrand());
  }

  setAddressSource(mode: string): void {
    const m = mode === 'saved' ? 'saved' : 'new';
    if (m === 'saved' && !this.profile()?.addresses?.length) {
      return;
    }
    this.addressSource.set(m);
    if (m === 'saved') {
      this.addressForm.disable({ emitEvent: false });
      const p = this.profile();
      if (p?.addresses?.length) {
        const def =
          p.addresses.find((a) => a.is_default) ?? p.addresses[0];
        this.selectedAddressId.set(def.id);
      }
    } else {
      this.addressForm.enable({ emitEvent: false });
    }
  }

  setCardSource(mode: string): void {
    const m = mode === 'saved' ? 'saved' : 'new';
    if (m === 'saved' && !this.profile()?.payment_methods?.length) {
      return;
    }
    this.cardSource.set(m);
    if (m === 'saved') {
      this.paymentForm.patchValue({
        card_number: '',
        expiry: '',
        card_holder: '',
      });
      const p = this.profile();
      if (p?.payment_methods?.length) {
        const pm =
          p.payment_methods.find((x) => x.is_default) ??
          p.payment_methods[0];
        this.selectedPaymentMethodId.set(pm.id);
      }
    }
    this.syncPaymentValidators();
  }

  syncPaymentValidators(): void {
    const cardNumber = this.paymentForm.get('card_number')!;
    const expiry = this.paymentForm.get('expiry')!;
    const holder = this.paymentForm.get('card_holder')!;
    const cvv = this.paymentForm.get('cvv')!;
    if (this.cardSource() === 'saved') {
      cardNumber.clearValidators();
      expiry.clearValidators();
      holder.clearValidators();
      cvv.setValidators([
        Validators.required,
        Validators.pattern(/^\d{3,4}$/),
      ]);
    } else {
      cardNumber.setValidators([
        Validators.required,
        this.cardNumberValidator,
      ]);
      expiry.setValidators([
        Validators.required,
        Validators.pattern(/^\d{2}\/\d{2}$/),
      ]);
      holder.setValidators([
        Validators.required,
        Validators.minLength(3),
      ]);
      cvv.setValidators([
        Validators.required,
        Validators.pattern(/^\d{3,4}$/),
      ]);
    }
    [cardNumber, expiry, holder, cvv].forEach((c) =>
      c.updateValueAndValidity({ emitEvent: false })
    );
  }

  setPaymentMode(mode: 'mock' | 'stripe'): void {
    if (mode === 'mock') {
      this.cardElement?.destroy();
      this.cardElement = null;
    }
    this.paymentMode.set(mode);
    if (mode === 'stripe' && this.stripeEnabled()) {
      setTimeout(() => this.mountStripeCard(), 0);
    }
  }

  private async mountStripeCard(): Promise<void> {
    const pk = this.stripePublishableKey();
    const el = this.stripeMount?.nativeElement;
    if (!pk || !el) return;
    if (this.cardElement) return;

    this.stripe = await loadStripe(pk);
    if (!this.stripe) return;

    const elements = this.stripe.elements({
      appearance: { theme: 'stripe' },
    });
    this.cardElement = elements.create('card', { hidePostalCode: true });
    this.cardElement.mount(el);
  }

  private cardNumberValidator = (
    control: AbstractControl
  ): ValidationErrors | null => {
    const raw = String(control.value ?? '').replace(/\s/g, '');
    if (!raw.length) return { required: true };
    if (!/^\d+$/.test(raw)) return { digits: true };
    const brand = detectCardBrand(raw);
    if (raw.length < 13) return { short: true };
    if (brand === 'unknown') {
      if (raw.length < 13 || raw.length > 19) return { length: true };
    } else {
      const expected = expectedCardLength(brand);
      if (raw.length !== expected) return { length: true };
    }
    if (!luhnCheck(raw)) return { luhn: true };
    return null;
  };

  formatCardNumber(event: Event): void {
    const input = event.target as HTMLInputElement;
    const value = input.value.replace(/\D/g, '').slice(0, 19);
    const brand = detectCardBrand(value);
    this.cardBrand.set(brand);
    const maxLen = brand === 'unknown' ? 19 : expectedCardLength(brand);
    const trimmed = value.slice(0, maxLen);
    const formatted = formatCardDisplay(trimmed);
    this.paymentForm.get('card_number')?.setValue(formatted, { emitEvent: false });
    const exp = expectedCardLength(brand);
    const cvvCtrl = this.paymentForm.get('cvv');
    if (brand === 'amex') {
      cvvCtrl?.setValidators([
        Validators.required,
        Validators.pattern(/^\d{4}$/),
      ]);
    } else {
      cvvCtrl?.setValidators([
        Validators.required,
        Validators.pattern(/^\d{3,4}$/),
      ]);
    }
    cvvCtrl?.updateValueAndValidity({ emitEvent: false });
  }

  formatExpiry(event: Event): void {
    const input = event.target as HTMLInputElement;
    const value = input.value.replace(/\D/g, '').substring(0, 4);
    const formatted =
      value.length > 2 ? `${value.slice(0, 2)}/${value.slice(2)}` : value;
    this.paymentForm.get('expiry')?.setValue(formatted, { emitEvent: false });
  }

  openMapsPreview(): void {
    const v = this.addressForm.getRawValue();
    const parts = [
      v.line1,
      v.line2,
      v.postal_code,
      v.city,
      v.state,
      v.country,
    ].filter(Boolean);
    if (!parts.length) return;
    const q = encodeURIComponent(parts.join(', '));
    window.open(`https://www.google.com/maps/search/?api=1&query=${q}`, '_blank');
  }

  private buildShippingAddress() {
    const v = this.addressForm.getRawValue();
    const lat = v.latitude?.toString().trim();
    const lng = v.longitude?.toString().trim();
    const latN = lat ? parseFloat(lat) : NaN;
    const lngN = lng ? parseFloat(lng) : NaN;
    return {
      full_name: v.full_name.trim(),
      line1: v.line1.trim(),
      line2: v.line2?.trim() || null,
      city: v.city.trim(),
      state: v.state.trim(),
      postal_code: v.postal_code.trim(),
      country: (v.country || 'ES').toUpperCase(),
      phone: v.phone?.trim() || null,
      latitude: lat && !Number.isNaN(latN) ? latN : null,
      longitude: lng && !Number.isNaN(lngN) ? lngN : null,
    };
  }

  private validateAddressForSubmit(): boolean {
    if (this.addressSource() === 'saved') {
      if (!this.selectedAddressId()) {
        this.snackBar.open('Selecciona una dirección', 'Cerrar', {
          duration: 4000,
        });
        return false;
      }
      return true;
    }
    this.addressForm.markAllAsTouched();
    if (this.addressForm.invalid) {
      return false;
    }
    return true;
  }

  private buildMockPayload(): Record<string, unknown> {
    const out: Record<string, unknown> = {};
    if (this.addressSource() === 'saved') {
      out['saved_address_id'] = this.selectedAddressId();
    } else {
      out['shipping_address'] = this.buildShippingAddress();
    }
    if (this.cardSource() === 'saved') {
      out['saved_payment_method_id'] = this.selectedPaymentMethodId();
      out['cvv'] = this.paymentForm.get('cvv')?.value;
      const h = this.paymentForm.get('card_holder')?.value?.trim();
      if (h) {
        out['card_holder'] = h;
      }
    } else {
      const rawCard = this.paymentForm.get('card_number')?.value.replace(/\s/g, '');
      out['card_number'] = rawCard;
      out['card_holder'] = this.paymentForm.get('card_holder')?.value;
      out['expiry'] = this.paymentForm.get('expiry')?.value;
      out['cvv'] = this.paymentForm.get('cvv')?.value;
    }
    return out;
  }

  onSubmitMock(): void {
    if (!this.validateAddressForSubmit()) {
      return;
    }

    this.paymentForm.markAllAsTouched();
    if (this.cardSource() === 'saved') {
      if (!this.selectedPaymentMethodId()) {
        this.snackBar.open('Selecciona una tarjeta', 'Cerrar', { duration: 4000 });
        return;
      }
    }
    if (this.paymentForm.invalid || this.loading()) {
      return;
    }

    this.loading.set(true);
    const payload = this.buildMockPayload();

    this.paymentService.checkout(payload as CheckoutRequest).subscribe({
      next: (result) => {
        this.loading.set(false);
        this.checkoutResult.set(result);
        if (result.payment.success) {
          this.cartService.resetLocal();
        }
      },
      error: (err) => {
        this.loading.set(false);
        const msg = err.error?.detail ?? 'Error al procesar el pedido';
        this.snackBar.open(msg, 'Cerrar', { duration: 5000, panelClass: ['snack-error'] });
      },
    });
  }

  async onSubmitStripe(): Promise<void> {
    if (!this.validateAddressForSubmit()) {
      return;
    }

    await this.mountStripeCard();
    if (!this.stripe || !this.cardElement) {
      this.snackBar.open('Stripe no está listo. Revisa la clave publicable.', 'Cerrar', {
        duration: 5000,
      });
      return;
    }

    this.loading.set(true);
    const shipBody =
      this.addressSource() === 'saved'
        ? { saved_address_id: this.selectedAddressId()! }
        : { shipping_address: this.buildShippingAddress() };

    this.paymentService.createStripePaymentIntent(shipBody).subscribe({
      next: async (intent) => {
        try {
          const { error, paymentIntent } = await this.stripe!.confirmCardPayment(
            intent.client_secret,
            {
              payment_method: {
                card: this.cardElement!,
              },
            }
          );

          if (error || !paymentIntent) {
            this.loading.set(false);
            this.snackBar.open(
              error?.message ?? 'No se pudo completar el pago',
              'Cerrar',
              { duration: 6000 }
            );
            return;
          }

          this.paymentService.confirmStripePayment(paymentIntent.id).subscribe({
            next: (res) => {
              this.loading.set(false);
              this.checkoutResult.set({
                order: res.order,
                payment: {
                  success: true,
                  status: 'success',
                  message: 'Pago con Stripe completado.',
                  transaction_id: res.payment_intent_id,
                },
              });
              this.cartService.resetLocal();
            },
            error: (err) => {
              this.loading.set(false);
              const msg = err.error?.detail ?? 'Error al confirmar el pedido';
              this.snackBar.open(msg, 'Cerrar', { duration: 5000 });
            },
          });
        } catch {
          this.loading.set(false);
          this.snackBar.open('Error de Stripe', 'Cerrar', { duration: 5000 });
        }
      },
      error: (err) => {
        this.loading.set(false);
        const msg = err.error?.detail ?? 'No se pudo iniciar el pago';
        this.snackBar.open(msg, 'Cerrar', { duration: 5000 });
      },
    });
  }

  onPay(): void {
    if (this.paymentMode() === 'stripe' && this.stripeEnabled()) {
      void this.onSubmitStripe();
    } else {
      this.onSubmitMock();
    }
  }
}
