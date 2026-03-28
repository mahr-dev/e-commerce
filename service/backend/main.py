"""
eCommerce API — FastAPI Application Entry Point

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

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
# CORS (ASGI): debe envolver también respuestas de error (p. ej. 401)
# ---------------------------------------------------------------------------

_CORS_HEADERS = {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD",
    "access-control-allow-headers": (
        "Authorization, Content-Type, Accept, Origin, X-Requested-With, "
        "access-control-request-method, access-control-request-headers"
    ),
    "access-control-max-age": "86400",
}


def _with_cors(response: JSONResponse) -> JSONResponse:
    for k, v in _CORS_HEADERS.items():
        response.headers[k] = v
    return response


@app.exception_handler(HTTPException)
async def http_exception_with_cors(_request: Request, exc: HTTPException) -> JSONResponse:
    """401/403/etc. deben llevar CORS o el navegador solo muestra error de CORS."""
    base = dict(exc.headers) if exc.headers else {}
    r = JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=base)
    return _with_cors(r)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint for Docker and load balancers."""
    return {"status": "ok", "service": "ecommerce-api", "version": "1.0.0"}
