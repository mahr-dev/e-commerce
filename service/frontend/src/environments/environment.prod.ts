export const environment = {
  production: true,
  /**
   * Mismo origen en Vercel: /api → rewrite al backend (ver service/frontend/vercel.json).
   * Si defines API_PUBLIC_URL en el build, inject-api-url.cjs usa URL directa (requiere CORS en API).
   */
  apiUrl: '/api',
};
