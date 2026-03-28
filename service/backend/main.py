"""
eCommerce API — FastAPI Application Entry Point

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from routers import auth, products, cart, checkout, orders, payment, account

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

# ---------------------------------------------------------------------------
# CORS: middleware explícito (preflight + cabeceras en la respuesta)
# ---------------------------------------------------------------------------
# CORSMiddleware con allow_headers=["*"] falla en algunos preflights; esto
# replica el origen pedido y devuelve cabeceras concretas en OPTIONS.


class OpenCorsMiddleware(BaseHTTPMiddleware):
    _allow_origin = "*"
    _allow_methods = "GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD"
    _default_allow_headers = (
        "Authorization, Content-Type, Accept, Origin, "
        "X-Requested-With, access-control-allow-origin, "
        "access-control-allow-headers, access-control-request-method, "
        "access-control-request-headers"
    )

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            req_h = request.headers.get("access-control-request-headers")
            allow_headers = (
                req_h if req_h else self._default_allow_headers
            )
            return Response(
                status_code=204,
                headers={
                    "access-control-allow-origin": self._allow_origin,
                    "access-control-allow-methods": self._allow_methods,
                    "access-control-allow-headers": allow_headers,
                    "access-control-max-age": "86400",
                },
            )

        response = await call_next(request)
        response.headers["access-control-allow-origin"] = self._allow_origin
        response.headers["access-control-allow-methods"] = self._allow_methods
        return response


app.add_middleware(OpenCorsMiddleware)

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

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint for Docker and load balancers."""
    return {"status": "ok", "service": "ecommerce-api", "version": "1.0.0"}
