/**
 * Card brand detection from PAN prefix + Luhn (no network calls).
 * For UX only — real validation is done by the payment processor.
 */

export type CardBrand =
  | 'visa'
  | 'mastercard'
  | 'amex'
  | 'discover'
  | 'diners'
  | 'unknown';

export function detectCardBrand(digitsOnly: string): CardBrand {
  const d = digitsOnly.replace(/\D/g, '');
  if (!d.length) return 'unknown';

  const n = parseInt(d.slice(0, 6), 10);
  const c1 = parseInt(d[0], 10);
  const c2 = d.length >= 2 ? parseInt(d.slice(0, 2), 10) : -1;
  const c4 = d.length >= 4 ? parseInt(d.slice(0, 4), 10) : -1;

  if (c1 === 4) return 'visa';
  if (c2 >= 51 && c2 <= 55) return 'mastercard';
  if (n >= 222100 && n <= 272099) return 'mastercard';
  if (c2 === 34 || c2 === 37) return 'amex';
  if (c4 === 6011 || c2 === 65) return 'discover';
  if (c2 === 36 || c2 === 38 || c2 === 39) return 'diners';

  return 'unknown';
}

/** Expected digit count for a complete number (best-effort). */
export function expectedCardLength(brand: CardBrand): number {
  switch (brand) {
    case 'amex':
      return 15;
    case 'diners':
      return 14;
    case 'unknown':
      return 16;
    default:
      return 16;
  }
}

/** Format PAN with spaces (Amex 4-6-5, others 4×4…). */
export function formatCardDisplay(digitsOnly: string): string {
  const d = digitsOnly.replace(/\D/g, '').slice(0, 19);
  const brand = detectCardBrand(d);
  if (brand === 'amex') {
    const p1 = d.slice(0, 4);
    const p2 = d.slice(4, 10);
    const p3 = d.slice(10, 15);
    return [p1, p2, p3].filter(Boolean).join(' ');
  }
  if (brand === 'diners' && d.length <= 14) {
    return d.replace(/(\d{4})(?=\d)/g, '$1 ').trim();
  }
  return d.replace(/(\d{4})(?=\d)/g, '$1 ');
}

export function luhnCheck(digitsOnly: string): boolean {
  const d = digitsOnly.replace(/\D/g, '');
  if (d.length < 13) return false;
  let sum = 0;
  let alt = false;
  for (let i = d.length - 1; i >= 0; i--) {
    let n = parseInt(d[i], 10);
    if (alt) {
      n *= 2;
      if (n > 9) n -= 9;
    }
    sum += n;
    alt = !alt;
  }
  return sum % 10 === 0;
}

export function cardBrandLabel(brand: CardBrand): string {
  const labels: Record<CardBrand, string> = {
    visa: 'Visa',
    mastercard: 'Mastercard',
    amex: 'American Express',
    discover: 'Discover',
    diners: 'Diners Club',
    unknown: 'Tarjeta',
  };
  return labels[brand];
}
