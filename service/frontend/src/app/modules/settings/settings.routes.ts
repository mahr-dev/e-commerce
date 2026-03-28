import { Routes } from '@angular/router';

export const SETTINGS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./settings-layout/settings-layout.component').then(
        (m) => m.SettingsLayoutComponent
      ),
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'informacion' },
      {
        path: 'informacion',
        loadComponent: () =>
          import('./settings-info/settings-info.component').then(
            (m) => m.SettingsInfoComponent
          ),
      },
      {
        path: 'pedidos',
        loadComponent: () =>
          import('../orders/order-history/order-history.component').then(
            (m) => m.OrderHistoryComponent
          ),
      },
      {
        path: 'direcciones',
        loadComponent: () =>
          import('./settings-addresses/settings-addresses.component').then(
            (m) => m.SettingsAddressesComponent
          ),
      },
      {
        path: 'pagos',
        loadComponent: () =>
          import('./settings-payment/settings-payment.component').then(
            (m) => m.SettingsPaymentComponent
          ),
      },
    ],
  },
];
