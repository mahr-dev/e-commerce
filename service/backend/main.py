"""
eCommerce API — FastAPI Application Entry Point

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
# Middleware
# ---------------------------------------------------------------------------

# Allow Angular dev server and production frontend to reach the API
ALLOWED_ORIGINS = [
    "http://localhost:4200",   # Angular dev server
    "http://localhost:80",     # Nginx explícito
    "http://localhost",        # Nginx en Docker (puerto 80 implícito)
    "http://frontend",         # Docker service name
]

_vercel = os.environ.get("VERCEL_URL")
if _vercel:
    ALLOWED_ORIGINS.append(f"https://{_vercel}")

for _origin in os.environ.get("CORS_EXTRA_ORIGINS", "").split(","):
    _o = _origin.strip()
    if _o:
        ALLOWED_ORIGINS.append(_o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router,     prefix="/auth",     tags=["Authentication"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(cart.router,     prefix="/cart",     tags=["Cart"])
app.include_router(checkout.router, prefix="/checkout", tags=["Checkout"])
app.include_router(orders.router,   prefix="/orders",   tags=["Orders"])
app.include_router(payment.router,  prefix="/payment",  tags=["Payment"])
app.include_router(account.router,  prefix="/account",  tags=["Account"])

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint for Docker and load balancers."""
    return {"status": "ok", "service": "ecommerce-api", "version": "1.0.0"}
