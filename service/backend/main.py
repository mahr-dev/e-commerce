"""
eCommerce API — FastAPI Application Entry Point

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

CORS: middleware propio que fuerza cabeceras en la respuesta final (en Vercel a veces
CORSMiddleware no deja Access-Control-Allow-Origin en el 200). No uses builds/routes
legacy con @vercel/python en vercel.json.
"""
import os
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

from routers import auth, products, cart, checkout, orders, payment, account

# ---------------------------------------------------------------------------
# Orígenes permitidos (allow_credentials=True → origen reflejado, no "*")
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

_VERCEL_APP_ORIGIN = re.compile(r"^https://[\w-]+\.vercel\.app$")

_CORS_METHODS = "GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD"


def _resolve_allowed_origin(request: StarletteRequest) -> str | None:
    raw = request.headers.get("origin")
    if not raw:
        return None
    origin = raw.strip()
    if origin in ALLOW_ORIGINS or _VERCEL_APP_ORIGIN.match(origin):
        return origin
    return None


class StrictCorsMiddleware(BaseHTTPMiddleware):
    """Preflight OPTIONS + cabeceras CORS en todas las respuestas permitidas."""

    async def dispatch(self, request: StarletteRequest, call_next):
        origin = _resolve_allowed_origin(request)

        if request.method == "OPTIONS":
            if origin is None:
                return await call_next(request)
            req_headers = request.headers.get("access-control-request-headers")
            allow_headers = req_headers or "authorization, content-type, accept, origin, x-requested-with"
            return Response(
                status_code=204,
                headers={
                    "access-control-allow-origin": origin,
                    "access-control-allow-credentials": "true",
                    "access-control-allow-methods": _CORS_METHODS,
                    "access-control-allow-headers": allow_headers,
                    "access-control-max-age": "86400",
                    "vary": "Origin",
                },
            )

        response = await call_next(request)
        if origin is not None:
            response.headers["access-control-allow-origin"] = origin
            response.headers["access-control-allow-credentials"] = "true"
            response.headers["access-control-allow-methods"] = _CORS_METHODS
            existing = response.headers.get("vary", "")
            parts = [p.strip() for p in existing.split(",") if p.strip()] if existing else []
            if not any(p.lower() == "origin" for p in parts):
                parts.append("Origin")
            response.headers["vary"] = ", ".join(parts)
        return response


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

app.add_middleware(StrictCorsMiddleware)


def _cors_headers_for_request(request: Request) -> dict[str, str]:
    o = _resolve_allowed_origin(request)
    if not o:
        return {}
    return {
        "access-control-allow-origin": o,
        "access-control-allow-credentials": "true",
        "access-control-allow-methods": _CORS_METHODS,
        "vary": "Origin",
    }


@app.exception_handler(HTTPException)
async def http_exception_with_cors(request: Request, exc: HTTPException) -> JSONResponse:
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
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(checkout.router, prefix="/checkout", tags=["Checkout"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(payment.router, prefix="/payment", tags=["Payment"])
app.include_router(account.router, prefix="/account", tags=["Account"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint for Docker and load balancers."""
    return {"status": "ok", "service": "ecommerce-api", "version": "1.0.0"}
