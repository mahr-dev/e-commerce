/**
 * Si existe API_PUBLIC_URL (Vercel), genera environment.vercel.generated.ts.
 * Si no existe, copia environment.prod.ts para poder usar --configuration vercel igual.
 */
const fs = require("fs");
const path = require("path");

const envDir = path.join(__dirname, "..", "src", "environments");
const out = path.join(envDir, "environment.vercel.generated.ts");
const prodPath = path.join(envDir, "environment.prod.ts");

const raw = (process.env.API_PUBLIC_URL || "").trim().replace(/\/$/, "");

let body;
if (raw) {
  body = `/* Generado en build (API_PUBLIC_URL) */
export const environment = {
  production: true,
  apiUrl: ${JSON.stringify(raw)},
};
`;
  fs.writeFileSync(out, body, "utf8");
  console.log("API_PUBLIC_URL ->", raw);
} else {
  fs.copyFileSync(prodPath, out);
  console.log("Sin API_PUBLIC_URL: usando environment.prod.ts");
}
