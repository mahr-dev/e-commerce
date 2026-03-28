import { Routes } from '@angular/router';
import { authGuard, publicGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./modules/home/landing/landing.component').then(
        (m) => m.LandingComponent
      ),
  },

  // Public auth routes (redirect to home if already logged in)
  {
    path: 'auth',
    canActivate: [publicGuard],
    children: [
      {
        path: 'login',
        loadComponent: () =>
          import('./modules/auth/login/login.component').then(
            (m) => m.LoginComponent
          ),
      },
      {
        path: 'register',
        loadComponent: () =>
          import('./modules/auth/register/register.component').then(
            (m) => m.RegisterComponent
          ),
      },
      { path: '', redirectTo: 'login', pathMatch: 'full' },
    ],
  },

  // Public product catalog
  {
    path: 'products',
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./modules/products/product-list/product-list.component').then(
            (m) => m.ProductListComponent
          ),
      },
      {
        path: ':id',
        loadComponent: () =>
          import(
            './modules/products/product-detail/product-detail.component'
          ).then((m) => m.ProductDetailComponent),
      },
    ],
  },

  // Protected routes (require login)
  {
    path: 'cart',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modules/cart/cart/cart.component').then(
        (m) => m.CartComponent
      ),
  },
  {
    path: 'checkout',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modules/checkout/checkout/checkout.component').then(
        (m) => m.CheckoutComponent
      ),
  },
  {
    path: 'orders',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./modules/orders/order-history/order-history.component').then(
        (m) => m.OrderHistoryComponent
      ),
  },
  {
    path: 'cuenta',
    canActivate: [authGuard],
    loadChildren: () =>
      import('./modules/settings/settings.routes').then((m) => m.SETTINGS_ROUTES),
  },

  // 404 fallback
  {
    path: '**',
    redirectTo: '/',
  },
];
