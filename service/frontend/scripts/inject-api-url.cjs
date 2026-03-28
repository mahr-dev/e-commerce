/**
 * - API_PUBLIC_URL definida → apiUrl = URL directa del backend (cross-origin + CORS en API).
 * - Sin API_PUBLIC_URL → apiUrl = '/api' (proxy en vercel.json, sin CORS en navegador).
 */
const fs = require("fs");
const path = require("path");

const envDir = path.join(__dirname, "..", "src", "environments");
const out = path.join(envDir, "environment.vercel.generated.ts");

const raw = (process.env.API_PUBLIC_URL || "").trim().replace(/\/$/, "");

const body = raw
  ? `/* Generado: API_PUBLIC_URL (llamada directa al backend) */
export const environment = {
  production: true,
  apiUrl: ${JSON.stringify(raw)},
};
`
  : `/* Generado: proxy /api → backend (vercel.json rewrites) */
export const environment = {
  production: true,
  apiUrl: '/api',
};
`;

fs.writeFileSync(out, body, "utf8");
console.log(raw ? `API_PUBLIC_URL -> ${raw}` : "apiUrl -> /api (proxy)");
