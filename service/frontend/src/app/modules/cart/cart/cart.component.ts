import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CartService } from '../../../core/services/cart.service';
import { CartItem } from '../../../shared/models/cart.model';

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDividerModule,
    MatTooltipModule,
  ],
  templateUrl: './cart.component.html',
  styleUrl: './cart.component.scss',
})
export class CartComponent implements OnInit {
  readonly loading = signal(true);
  readonly updatingItem = signal<string | null>(null);

  readonly cart = this.cartService.cart;
  readonly total = this.cartService.total;
  readonly itemCount = this.cartService.itemCount;

  constructor(
    public cartService: CartService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.cartService.loadCart().subscribe({
      next: () => this.loading.set(false),
      error: () => {
        this.loading.set(false);
        this.snackBar.open('Error al cargar el carrito', 'Cerrar', { duration: 3000 });
      },
    });
  }

  updateQuantity(item: CartItem, delta: number): void {
    const newQty = item.quantity + delta;
    if (newQty < 1) {
      this.removeItem(item);
      return;
    }

    this.updatingItem.set(item.product_id);
    this.cartService.updateQuantity(item.product_id, newQty).subscribe({
      next: () => this.updatingItem.set(null),
      error: (err) => {
        this.updatingItem.set(null);
        this.snackBar.open(
          err.error?.detail ?? 'Error al actualizar cantidad',
          'Cerrar',
          { duration: 3000 }
        );
      },
    });
  }

  removeItem(item: CartItem): void {
    this.updatingItem.set(item.product_id);
    this.cartService.removeItem(item.product_id).subscribe({
      next: () => {
        this.updatingItem.set(null);
        this.snackBar.open(`"${item.name}" eliminado del carrito`, 'Deshacer', {
          duration: 3000,
        });
      },
      error: () => {
        this.updatingItem.set(null);
        this.snackBar.open('Error al eliminar el producto', 'Cerrar', { duration: 3000 });
      },
    });
  }

  clearCart(): void {
    this.cartService.clearCart().subscribe({
      next: () => {
        this.snackBar.open('Carrito vaciado', 'Cerrar', { duration: 2000 });
      },
    });
  }

  getItemSubtotal(item: CartItem): number {
    return item.price * item.quantity;
  }
}
