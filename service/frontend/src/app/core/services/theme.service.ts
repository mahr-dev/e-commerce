import { Injectable, signal, effect } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly _isDark = signal<boolean>(
    localStorage.getItem('theme') === 'dark' ||
    (!localStorage.getItem('theme') &&
      window.matchMedia('(prefers-color-scheme: dark)').matches)
  );

  readonly isDark = this._isDark.asReadonly();

  constructor() {
    // Apply on <html> and <body> so Material overlays and :root inherit correctly
    effect(() => {
      const dark = this._isDark();
      document.documentElement.classList.toggle('dark-mode', dark);
      document.body.classList.toggle('dark-mode', dark);
      localStorage.setItem('theme', dark ? 'dark' : 'light');
    });
  }

  toggle(): void {
    this._isDark.update((v) => !v);
  }
}
