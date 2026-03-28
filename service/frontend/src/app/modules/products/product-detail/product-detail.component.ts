import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { ProductService } from '../../../core/services/product.service';
import { CartService } from '../../../core/services/cart.service';
import { AuthService } from '../../../core/services/auth.service';
import { Product } from '../../../shared/models/product.model';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDividerModule,
    MatChipsModule,
  ],
  templateUrl: './product-detail.component.html',
  styleUrl: './product-detail.component.scss',
})
export class ProductDetailComponent implements OnInit {
  readonly product = signal<Product | null>(null);
  readonly loading = signal(true);
  readonly addingToCart = signal(false);
  quantity = 1;

  readonly isAuthenticated = this.authService.isAuthenticated;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private productService: ProductService,
    private cartService: CartService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.router.navigate(['/products']);
      return;
    }

    this.productService.getById(id).subscribe({
      next: (p) => {
        this.product.set(p);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.snackBar.open('Producto no encontrado', 'Cerrar', { duration: 3000 });
        this.router.navigate(['/products']);
      },
    });
  }

  increaseQty(): void {
    const p = this.product();
    if (p && this.quantity < p.stock) this.quantity++;
  }

  decreaseQty(): void {
    if (this.quantity > 1) this.quantity--;
  }

  addToCart(): void {
    const p = this.product();
    if (!p || this.addingToCart()) return;

    if (!this.isAuthenticated()) {
      this.snackBar.open('Inicia sesión para agregar al carrito', 'Login', {
        duration: 4000,
      });
      this.router.navigate(['/auth/login']);
      return;
    }

    this.addingToCart.set(true);
    this.cartService.addItem({ product_id: p.id, quantity: this.quantity }).subscribe({
      next: () => {
        this.addingToCart.set(false);
        this.snackBar.open(
          `${this.quantity}x "${p.name}" agregado al carrito`,
          'Ver carrito',
          { duration: 3000 }
        );
      },
      error: (err) => {
        this.addingToCart.set(false);
        const msg = err.error?.detail ?? 'Error al agregar al carrito';
        this.snackBar.open(msg, 'Cerrar', { duration: 3000 });
      },
    });
  }
}
