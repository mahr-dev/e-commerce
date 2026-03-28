import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ProductService } from '../../../core/services/product.service';
import { CartService } from '../../../core/services/cart.service';
import { AuthService } from '../../../core/services/auth.service';
import { Product } from '../../../shared/models/product.model';

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
  ],
  templateUrl: './product-list.component.html',
  styleUrl: './product-list.component.scss',
})
export class ProductListComponent implements OnInit {
  readonly products = signal<Product[]>([]);
  readonly categories = signal<string[]>([]);
  readonly loading = signal(false);
  readonly addingToCart = signal<string | null>(null);

  searchQuery = '';
  selectedCategory = '';

  readonly isAuthenticated = this.authService.isAuthenticated;

  constructor(
    private productService: ProductService,
    private cartService: CartService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadProducts();
    this.loadCategories();
  }

  loadProducts(): void {
    this.loading.set(true);
    const filters: { search?: string; category?: string } = {};
    if (this.searchQuery) filters.search = this.searchQuery;
    if (this.selectedCategory) filters.category = this.selectedCategory;

    this.productService.getAll(filters).subscribe({
      next: (products) => {
        this.products.set(products);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.snackBar.open('Error al cargar productos', 'Cerrar', {
          duration: 3000,
        });
      },
    });
  }

  loadCategories(): void {
    this.productService.getCategories().subscribe({
      next: (cats) => this.categories.set(cats),
    });
  }

  onSearch(): void {
    this.loadProducts();
  }

  onCategoryChange(): void {
    this.loadProducts();
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.selectedCategory = '';
    this.loadProducts();
  }

  addToCart(product: Product, event: Event): void {
    event.stopPropagation();
    event.preventDefault();

    if (!this.isAuthenticated()) {
      this.snackBar.open('Inicia sesión para agregar productos al carrito', 'Login', {
        duration: 4000,
      });
      return;
    }

    if (product.stock === 0) return;

    this.addingToCart.set(product.id);
    this.cartService.addItem({ product_id: product.id, quantity: 1 }).subscribe({
      next: () => {
        this.addingToCart.set(null);
        this.snackBar.open(`"${product.name}" agregado al carrito`, 'Ver carrito', {
          duration: 3000,
        });
      },
      error: (err) => {
        this.addingToCart.set(null);
        const msg = err.error?.detail ?? 'Error al agregar al carrito';
        this.snackBar.open(msg, 'Cerrar', { duration: 3000 });
      },
    });
  }
}
