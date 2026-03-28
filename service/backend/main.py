"""
eCommerce API — FastAPI Application Entry Point

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Swagger UI:  http://localhost:8000/api/docs
ReDoc:       http://localhost:8000/api/redoc

La API REST vive bajo el prefijo /api (mismo origen que el front en Vercel).
"""
import mimetypes
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from routers import auth, products, cart, checkout, orders, payment, account

# ---------------------------------------------------------------------------
# API (montada en /api)
# ---------------------------------------------------------------------------

api_app = FastAPI(
    title="eCommerce API",
    description=(
        "RESTful API for a full-stack eCommerce application. "
        "Includes product catalog, shopping cart, mock payment processing, and order management."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow Angular dev server and production frontend to reach the API
ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://localhost:80",
    "http://localhost",
    "http://frontend",
]

_vercel = os.environ.get("VERCEL_URL")
if _vercel:
    ALLOWED_ORIGINS.append(f"https://{_vercel}")

for _origin in os.environ.get("CORS_EXTRA_ORIGINS", "").split(","):
    _o = _origin.strip()
    if _o:
        ALLOWED_ORIGINS.append(_o)

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_app.include_router(products.router, prefix="/products", tags=["Products"])
api_app.include_router(cart.router, prefix="/cart", tags=["Cart"])
api_app.include_router(checkout.router, prefix="/checkout", tags=["Checkout"])
api_app.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_app.include_router(payment.router, prefix="/payment", tags=["Payment"])
api_app.include_router(account.router, prefix="/account", tags=["Account"])


@api_app.get("/health", tags=["Health"])
async def health_check():
    """Health check (ruta canónica bajo /api en despliegue unificado)."""
    return {"status": "ok", "service": "ecommerce-api", "version": "1.0.0"}

# ---------------------------------------------------------------------------
# Raíz: montaje /api + estáticos Angular (public/) + SPA fallback
# ---------------------------------------------------------------------------

PUBLIC_DIR = Path(__file__).resolve().parent.parent.parent / "public"


def _safe_public_file(relative: str) -> Path | None:
    if not relative or relative.startswith("..") or "\\..\\" in relative:
        return None
    candidate = (PUBLIC_DIR / relative).resolve()
    try:
        candidate.relative_to(PUBLIC_DIR.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _file_response_inline(path: Path) -> FileResponse:
    """FileResponse con inline (Starlette por defecto usa attachment → el navegador descarga)."""
    ext = path.suffix.lower()
    if ext == ".html":
        media_type = "text/html; charset=utf-8"
    elif ext == ".js":
        media_type = "application/javascript; charset=utf-8"
    elif ext == ".css":
        media_type = "text/css; charset=utf-8"
    elif ext == ".json":
        media_type = "application/json; charset=utf-8"
    elif ext == ".svg":
        media_type = "image/svg+xml"
    elif ext == ".ico":
        media_type = "image/x-icon"
    else:
        guessed, _ = mimetypes.guess_type(path.name)
        media_type = guessed or "application/octet-stream"
    return FileResponse(
        path,
        media_type=media_type,
        content_disposition_type="inline",
    )


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/api", api_app)


@app.get("/health", include_in_schema=False, tags=["Health"])
async def health_check_docker():
    """Misma respuesta que /api/health; útil para Docker sin prefijo."""
    return {"status": "ok", "service": "ecommerce-api", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
async def serve_index_root():
    """Raíz explícita (algunos despliegues no matchean bien el catch-all vacío)."""
    index = PUBLIC_DIR / "index.html"
    if index.is_file():
        return _file_response_inline(index)
    return Response(status_code=404)


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    """Sirve ficheros de `public/` o `index.html` para rutas del SPA."""
    if full_path.startswith("api"):
        return Response(status_code=404)
    f = _safe_public_file(full_path)
    if f is not None:
        return _file_response_inline(f)
    index = PUBLIC_DIR / "index.html"
    if index.is_file():
        return _file_response_inline(index)
    return Response(status_code=404)
