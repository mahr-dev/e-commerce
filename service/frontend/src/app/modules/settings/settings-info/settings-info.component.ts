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
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AccountService } from '../../../core/services/account.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-settings-info',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
  ],
  templateUrl: './settings-info.component.html',
  styleUrl: './settings-info.component.scss',
})
export class SettingsInfoComponent implements OnInit {
  readonly loading = signal(true);
  readonly saving = signal(false);

  readonly form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: [{ value: '', disabled: true }],
    phone: [''],
  });

  constructor(
    private fb: FormBuilder,
    private accountService: AccountService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.accountService.getProfile().subscribe({
      next: (p) => {
        this.form.patchValue({
          name: p.name,
          email: p.email,
          phone: p.phone ?? '',
        });
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.snackBar.open('No se pudo cargar el perfil', 'Cerrar', {
          duration: 4000,
        });
      },
    });
  }

  save(): void {
    if (this.form.invalid || this.saving()) return;
    this.saving.set(true);
    const v = this.form.getRawValue();
    this.accountService
      .updateProfile({
        name: v.name?.trim(),
        phone: v.phone?.trim() || null,
      })
      .subscribe({
        next: (p) => {
          this.saving.set(false);
          this.authService.patchLocalUser({
            name: p.name,
            phone: p.phone ?? null,
          });
          this.snackBar.open('Perfil actualizado', 'OK', { duration: 2500 });
        },
        error: (err) => {
          this.saving.set(false);
          const msg = err.error?.detail ?? 'Error al guardar';
          this.snackBar.open(msg, 'Cerrar', { duration: 4000 });
        },
      });
  }
}
