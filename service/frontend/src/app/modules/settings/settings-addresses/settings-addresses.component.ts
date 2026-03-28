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
import { SavedAddress } from '../../../shared/models/account.model';

@Component({
  selector: 'app-settings-addresses',
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
  templateUrl: './settings-addresses.component.html',
  styleUrl: './settings-addresses.component.scss',
})
export class SettingsAddressesComponent implements OnInit {
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly addresses = signal<SavedAddress[]>([]);
  readonly editingId = signal<string | null>(null);

  readonly form = this.fb.group({
    label: ['', Validators.required],
    full_name: ['', Validators.required],
    line1: ['', [Validators.required, Validators.minLength(3)]],
    line2: [''],
    city: ['', Validators.required],
    state: ['', Validators.required],
    postal_code: ['', Validators.required],
    country: ['ES', Validators.required],
    phone: [''],
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
        this.addresses.set((p.addresses ?? []) as SavedAddress[]);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.snackBar.open('Error al cargar direcciones', 'Cerrar', {
          duration: 4000,
        });
      },
    });
  }

  startAdd(): void {
    this.editingId.set(null);
    this.form.reset({
      label: '',
      full_name: '',
      line1: '',
      line2: '',
      city: '',
      state: '',
      postal_code: '',
      country: 'ES',
      phone: '',
      is_default: false,
    });
  }

  startEdit(a: SavedAddress): void {
    this.editingId.set(a.id);
    this.form.patchValue({
      label: a.label,
      full_name: a.full_name,
      line1: a.line1,
      line2: a.line2 ?? '',
      city: a.city,
      state: a.state,
      postal_code: a.postal_code,
      country: a.country,
      phone: a.phone ?? '',
      is_default: a.is_default,
    });
  }

  cancelForm(): void {
    this.editingId.set(null);
    this.startAdd();
  }

  submit(): void {
    if (this.form.invalid || this.saving()) return;
    this.saving.set(true);
    const v = this.form.getRawValue();
    const body = {
      label: v.label!.trim(),
      full_name: v.full_name!.trim(),
      line1: v.line1!.trim(),
      line2: v.line2?.trim() || null,
      city: v.city!.trim(),
      state: v.state!.trim(),
      postal_code: v.postal_code!.trim(),
      country: v.country!,
      phone: v.phone?.trim() || null,
      is_default: !!v.is_default,
    };

    const id = this.editingId();
    const req$ = id
      ? this.accountService.updateAddress(id, body)
      : this.accountService.addAddress(body);

    req$.subscribe({
      next: () => {
        this.saving.set(false);
        this.snackBar.open(id ? 'Dirección actualizada' : 'Dirección guardada', 'OK', {
          duration: 2500,
        });
        this.cancelForm();
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

  remove(a: SavedAddress): void {
    if (!confirm('¿Eliminar esta dirección?')) return;
    this.accountService.deleteAddress(a.id).subscribe({
      next: () => {
        this.snackBar.open('Dirección eliminada', 'OK', { duration: 2500 });
        this.reload();
      },
      error: () =>
        this.snackBar.open('No se pudo eliminar', 'Cerrar', { duration: 4000 }),
    });
  }
}
