/**
 * Build Vercel: apiUrl absoluta https://<VERCEL_URL>/api para que en Network aparezca
 * p. ej. https://e-commerce-txvg.vercel.app/api/products/... (mismo origen que el front).
 * En local (sin VERCEL_URL) → '/api'.
 * El destino real del API sigue siendo el rewrite en service/frontend/vercel.json.
 */
const fs = require("fs");
const path = require("path");

const envDir = path.join(__dirname, "..", "src", "environments");
const out = path.join(envDir, "environment.vercel.generated.ts");

if ((process.env.API_PUBLIC_URL || "").trim()) {
  console.warn(
    "API_PUBLIC_URL está definida pero se ignora: usa VERCEL_URL + /api o '/api' en local."
  );
}

const explicit = (process.env.PUBLIC_APP_URL || "").trim().replace(/\/$/, "");
const vercelHost = (process.env.VERCEL_URL || "")
  .trim()
  .replace(/^https?:\/\//, "");

let apiUrl;
if (explicit) {
  apiUrl = `${explicit}/api`;
} else if (vercelHost) {
  apiUrl = `https://${vercelHost}/api`;
} else {
  apiUrl = "/api";
}

const body = `/* Generado por inject-api-url.cjs (${apiUrl.startsWith("https") ? "origen Vercel" : "relativo /api"}) */
export const environment = {
  production: true,
  apiUrl: ${JSON.stringify(apiUrl)},
};
`;

fs.writeFileSync(out, body, "utf8");
console.log(`apiUrl -> ${apiUrl}`);
