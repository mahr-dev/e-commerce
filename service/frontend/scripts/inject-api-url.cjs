/**
 * Build Vercel: siempre apiUrl = '/api' (mismo origen que la página → sin CORS en el navegador).
 * El proxy en vercel.json reenvía al backend; no uses URL absoluta del front aquí (previews / otros hosts fallan).
 * API_PUBLIC_URL se ignora si está definida.
 */
const fs = require("fs");
const path = require("path");

const envDir = path.join(__dirname, "..", "src", "environments");
const out = path.join(envDir, "environment.vercel.generated.ts");

if ((process.env.API_PUBLIC_URL || "").trim()) {
  console.warn(
    "API_PUBLIC_URL está definida pero se ignora: el front usa solo /api (mismo origen, sin CORS)."
  );
}

const body = `/* Generado por inject-api-url.cjs: /api en el mismo host que el SPA */
export const environment = {
  production: true,
  apiUrl: '/api',
};
`;

fs.writeFileSync(out, body, "utf8");
console.log("apiUrl -> /api (mismo origen)");
