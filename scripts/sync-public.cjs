const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const src = path.join(
  root,
  "service",
  "frontend",
  "dist",
  "ecommerce-frontend",
  "browser"
);
const dest = path.join(root, "public");

function copyDir(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const name of fs.readdirSync(from)) {
    const fromPath = path.join(from, name);
    const toPath = path.join(to, name);
    if (fs.statSync(fromPath).isDirectory()) {
      copyDir(fromPath, toPath);
    } else {
      fs.copyFileSync(fromPath, toPath);
    }
  }
}

if (!fs.existsSync(src)) {
  console.error("Missing Angular output:", src);
  process.exit(1);
}

fs.rmSync(dest, { recursive: true, force: true });
copyDir(src, dest);
