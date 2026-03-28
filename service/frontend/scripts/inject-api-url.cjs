/**
 * Build Vercel: siempre apiUrl = '/api' (mismo origen; proxy en vercel.json → backend).
 * API_PUBLIC_URL en el dashboard se ignora a propósito para no exponer llamadas directas al API.
 */
const fs = require("fs");
const path = require("path");

const envDir = path.join(__dirname, "..", "src", "environments");
const out = path.join(envDir, "environment.vercel.generated.ts");

if ((process.env.API_PUBLIC_URL || "").trim()) {
  console.warn(
    "API_PUBLIC_URL está definida pero se ignora: el front usa solo /api (proxy). Elimínala en Vercel para evitar confusiones."
  );
}

const body = `/* Generado por inject-api-url.cjs: proxy /api (ver service/frontend/vercel.json) */
export const environment = {
  production: true,
  apiUrl: '/api',
};
`;

fs.writeFileSync(out, body, "utf8");
console.log("apiUrl -> /api (proxy Vercel)");
