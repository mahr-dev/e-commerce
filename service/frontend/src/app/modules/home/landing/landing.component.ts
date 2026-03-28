import {
  Component,
  OnInit,
  signal,
  ElementRef,
  viewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ProductService } from '../../../core/services/product.service';
import { AuthService } from '../../../core/services/auth.service';
import { Product } from '../../../shared/models/product.model';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.scss',
})
export class LandingComponent implements OnInit {
  readonly bestsellers = signal<Product[]>([]);
  readonly loadingBestsellers = signal(true);
  readonly isAuthenticated = this.authService.isAuthenticated;

  readonly sliderEl = viewChild<ElementRef<HTMLDivElement>>('bestsellerSlider');

  constructor(
    private productService: ProductService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.productService.getBestsellers(12).subscribe({
      next: (list) => {
        this.bestsellers.set(list);
        this.loadingBestsellers.set(false);
      },
      error: () => this.loadingBestsellers.set(false),
    });
  }

  scrollSlider(dir: -1 | 1): void {
    const el = this.sliderEl()?.nativeElement;
    if (!el) return;
    const slide = el.querySelector<HTMLElement>('.bestseller-slide');
    const step = slide ? slide.offsetWidth + 16 : 300;
    el.scrollBy({ left: dir * step, behavior: 'smooth' });
  }
}
