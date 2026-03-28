import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { OrderService } from '../../../core/services/order.service';
import { Order, ShippingAddress } from '../../../shared/models/order.model';

@Component({
  selector: 'app-order-history',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    MatDividerModule,
    MatChipsModule,
    MatSnackBarModule,
  ],
  templateUrl: './order-history.component.html',
  styleUrl: './order-history.component.scss',
})
export class OrderHistoryComponent implements OnInit {
  readonly orders = signal<Order[]>([]);
  readonly loading = signal(true);

  constructor(
    private orderService: OrderService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.orderService.getOrders().subscribe({
      next: (orders) => {
        this.orders.set(orders);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.snackBar.open('Error al cargar pedidos', 'Cerrar', { duration: 3000 });
      },
    });
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      pending: 'Pendiente',
      paid: 'Pagado',
      failed: 'Fallido',
      shipped: 'Enviado',
      cancelled: 'Cancelado',
    };
    return labels[status] ?? status;
  }

  getStatusIcon(status: string): string {
    const icons: Record<string, string> = {
      pending: 'schedule',
      paid: 'check_circle',
      failed: 'cancel',
      shipped: 'local_shipping',
      cancelled: 'block',
    };
    return icons[status] ?? 'help';
  }

  getOrderItemsTotal(order: Order): number {
    return order.items.reduce((sum, item) => sum + item.quantity, 0);
  }

  getShipping(order: Order): ShippingAddress | null {
    const s = order.shipping_address;
    if (!s || typeof s !== 'object' || !('line1' in s)) return null;
    return s as ShippingAddress;
  }

  formatAddressLine(order: Order): string | null {
    const a = this.getShipping(order);
    if (!a) return null;
    const parts = [
      a.line1,
      a.line2,
      `${a.postal_code} ${a.city}`,
      a.state,
      a.country,
    ].filter(Boolean);
    return parts.join(' · ');
  }
}
