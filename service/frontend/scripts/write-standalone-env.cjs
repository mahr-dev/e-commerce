/**
 * Genera environment.standalone.generated.ts desde API_PUBLIC_URL (Vercel / CI).
 * Sin barra final. Ej.: https://mi-api.vercel.app
 */
const fs = require("fs");
const path = require("path");

const raw = (process.env.API_PUBLIC_URL || "").trim().replace(/\/$/, "");
const out = path.join(__dirname, "..", "src", "environments", "environment.standalone.generated.ts");

if (!raw) {
  console.error(
    "Falta API_PUBLIC_URL (URL pública del backend, sin barra final). " +
      "Ej.: https://tu-backend.vercel.app"
  );
  process.exit(1);
}

const body = `/* Generado por scripts/write-standalone-env.cjs — no editar */
export const environment = {
  production: true,
  apiUrl: ${JSON.stringify(raw)},
};
`;

fs.writeFileSync(out, body, "utf8");
console.log("OK: apiUrl ->", raw);
