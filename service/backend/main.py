"""
eCommerce API — FastAPI Application Entry Point

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc

CORS: el middleware va antes de los routers. No uses builds/routes legacy
con @vercel/python en vercel.json: rompe el runtime ASGI en Vercel.
"""
import os
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, products, cart, checkout, orders, payment, account

# ---------------------------------------------------------------------------
# Orígenes permitidos (allow_credentials=True → no se puede usar "*")
# ---------------------------------------------------------------------------

ALLOW_ORIGINS = [
    "https://e-commerce-frontend-seven-self.vercel.app",
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:80",
    "http://localhost",
    "http://frontend",
]

_vercel = os.environ.get("VERCEL_URL")
if _vercel:
    ALLOW_ORIGINS.append(f"https://{_vercel}")

for _part in os.environ.get("CORS_EXTRA_ORIGINS", "").split(","):
    _o = _part.strip()
    if _o and _o not in ALLOW_ORIGINS:
        ALLOW_ORIGINS.append(_o)

# Previews u otros front en *.vercel.app
_VERCEL_APP_ORIGIN = re.compile(r"^https://[\w-]+\.vercel\.app$")

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="eCommerce API",
    description=(
        "RESTful API for a full-stack eCommerce application. "
        "Includes product catalog, shopping cart, mock payment processing, and order management."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS primero (antes de rutas y del resto de middlewares que añadas)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_origin_regex=r"https://[\w-]+\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
)


def _cors_headers_for_request(request: Request) -> dict[str, str]:
    """Con credentials, Allow-Origin debe ser el Origin concreto del request."""
    origin = request.headers.get("origin")
    if not origin:
        return {}
    if origin in ALLOW_ORIGINS or _VERCEL_APP_ORIGIN.match(origin):
        return {
            "access-control-allow-origin": origin,
            "access-control-allow-credentials": "true",
        }
    return {}


@app.exception_handler(HTTPException)
async def http_exception_with_cors(request: Request, exc: HTTPException) -> JSONResponse:
    """401/403 con las mismas reglas CORS (evita que el navegador solo muestre error de CORS)."""
    hdrs: dict[str, str] = {}
    if exc.headers:
        hdrs = {k: v for k, v in exc.headers.items()}
    hdrs.update(_cors_headers_for_request(request))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": jsonable_encoder(exc.detail)},
        headers=hdrs,
    )

# ---------------------------------------------------------------------------
# Routers (catálogo /products es público: sin Depends de auth en routers/products)
# ---------------------------------------------------------------------------

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(checkout.router, prefix="/checkout", tags=["Checkout"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(payment.router, prefix="/payment", tags=["Payment"])
app.include_router(account.router, prefix="/account", tags=["Account"])

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint for Docker and load balancers."""
    return {"status": "ok", "service": "ecommerce-api", "version": "1.0.0"}
