import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormBuilder,
  Validators,
} from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { AccountService } from '../../../core/services/account.service';
import { SavedPaymentMethod } from '../../../shared/models/account.model';

@Component({
  selector: 'app-settings-payment',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDividerModule,
    MatCheckboxModule,
  ],
  templateUrl: './settings-payment.component.html',
  styleUrl: './settings-payment.component.scss',
})
export class SettingsPaymentComponent implements OnInit {
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly methods = signal<SavedPaymentMethod[]>([]);

  readonly brands = [
    'Visa',
    'Mastercard',
    'American Express',
    'Discover',
    'Otra',
  ];

  readonly form = this.fb.group({
    brand: ['Visa', Validators.required],
    last4: [
      '',
      [Validators.required, Validators.pattern(/^\d{4}$/)],
    ],
    expiry: ['', [Validators.required, Validators.pattern(/^\d{2}\/\d{2}$/)]],
    label: [''],
    is_default: [false],
  });

  constructor(
    private fb: FormBuilder,
    private accountService: AccountService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.accountService.getProfile().subscribe({
      next: (p) => {
        this.methods.set(p.payment_methods ?? []);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.snackBar.open('Error al cargar métodos de pago', 'Cerrar', {
          duration: 4000,
        });
      },
    });
  }

  formatExpiry(ev: Event): void {
    const input = ev.target as HTMLInputElement;
    const v = input.value.replace(/\D/g, '').slice(0, 4);
    const formatted = v.length > 2 ? `${v.slice(0, 2)}/${v.slice(2)}` : v;
    this.form.get('expiry')?.setValue(formatted, { emitEvent: false });
  }

  submit(): void {
    if (this.form.invalid || this.saving()) return;
    this.saving.set(true);
    const v = this.form.getRawValue();
    this.accountService
      .addPaymentMethod({
        brand: v.brand!,
        last4: v.last4!,
        expiry: v.expiry!,
        label: v.label?.trim() || null,
        is_default: !!v.is_default,
      })
      .subscribe({
        next: () => {
          this.saving.set(false);
          this.snackBar.open('Método guardado (referencia de prueba)', 'OK', {
            duration: 3000,
          });
          this.form.reset({
            brand: 'Visa',
            last4: '',
            expiry: '',
            label: '',
            is_default: false,
          });
          this.reload();
        },
        error: (err) => {
          this.saving.set(false);
          this.snackBar.open(err.error?.detail ?? 'Error al guardar', 'Cerrar', {
            duration: 4000,
          });
        },
      });
  }

  remove(pm: SavedPaymentMethod): void {
    if (!confirm('¿Eliminar este método de pago?')) return;
    this.accountService.deletePaymentMethod(pm.id).subscribe({
      next: () => {
        this.snackBar.open('Eliminado', 'OK', { duration: 2500 });
        this.reload();
      },
      error: () =>
        this.snackBar.open('No se pudo eliminar', 'Cerrar', { duration: 4000 }),
    });
  }

  setDefault(pm: SavedPaymentMethod): void {
    this.accountService.setDefaultPaymentMethod(pm.id).subscribe({
      next: (profile) => {
        this.methods.set(profile.payment_methods ?? []);
        this.snackBar.open('Método predeterminado actualizado', 'OK', {
          duration: 2500,
        });
      },
      error: () =>
        this.snackBar.open('Error al actualizar', 'Cerrar', { duration: 4000 }),
    });
  }
}
