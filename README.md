# ShopNow — eCommerce Fullstack

Aplicación eCommerce completa con Angular 18 (frontend) y FastAPI (backend), base de datos simulada con archivos JSON y pasarela de pagos mock.

---

## Arquitectura

```
E-commerce/
├── backend/                  # FastAPI (Python)
│   ├── main.py               # Entry point + CORS + routers
│   ├── routers/              # Endpoints REST por dominio
│   ├── services/             # Lógica de negocio
│   ├── models/               # Pydantic schemas
│   ├── utils/                # JWT auth + file handler
│   └── data/                 # JSON "base de datos"
│       ├── products.json
│       ├── users.json
│       └── orders.json
│
└── frontend/                 # Angular 18 (standalone components)
    └── src/app/
        ├── core/
        │   ├── services/     # AuthService, CartService, etc.
        │   ├── guards/       # authGuard, publicGuard
        │   └── interceptors/ # authInterceptor (JWT)
        ├── shared/models/    # Interfaces TypeScript
        └── modules/
            ├── auth/         # Login, Register
            ├── products/     # ProductList, ProductDetail
            ├── cart/         # Cart
            ├── checkout/     # Checkout + payment form
            └── orders/       # OrderHistory
```

---

## Inicio rápido

### Backend (FastAPI)

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**API disponible en:** `http://localhost:8000`
**Swagger UI:** `http://localhost:8000/docs`

---

### Frontend (Angular)

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar dev server
ng serve
```

**App disponible en:** `http://localhost:4200`

---

### Docker (recomendado)

```bash
# En la raíz del proyecto
docker-compose up --build
```

- Frontend: `http://localhost:80`
- Backend: `http://localhost:8000`

---

## Credenciales de prueba

| Email                    | Password     | Rol   |
|--------------------------|--------------|-------|
| `admin@ecommerce.com`    | `admin`      | Admin |
| `john@example.com`       | `password123`| User  |

---

## Tarjetas de pago (simuladas)

| Número                  | Resultado       |
|-------------------------|-----------------|
| `4242 4242 4242 4242`   | Pago exitoso    |
| `4000 0000 0000 0002`   | Tarjeta rechazada|
| `4000 0000 0000 0077`   | Pago pendiente  |
| Cualquier otro (16 dígitos) | 90% exitoso / 10% fallido |

---

## Endpoints principales

| Método | Endpoint              | Auth | Descripción             |
|--------|-----------------------|------|-------------------------|
| POST   | `/auth/register`      | No   | Registro de usuario     |
| POST   | `/auth/login`         | No   | Login → JWT token       |
| GET    | `/products`           | No   | Listar productos        |
| GET    | `/products/{id}`      | No   | Detalle de producto     |
| GET    | `/cart`               | Sí   | Ver carrito             |
| POST   | `/cart`               | Sí   | Agregar al carrito      |
| DELETE | `/cart/{product_id}`  | Sí   | Quitar del carrito      |
| POST   | `/checkout`           | Sí   | Procesar pago + orden   |
| GET    | `/orders`             | Sí   | Historial de pedidos    |
| POST   | `/payment/process`    | No   | Test de pago directo    |

---

## Flujo completo

```
1. Usuario → /auth/login (POST) → recibe JWT token
2. Token se guarda en localStorage, interceptor lo adjunta en cada request
3. Usuario → /products (GET) → ve catálogo
4. Usuario → /cart (POST) { product_id, quantity } → agrega producto
5. Usuario → /checkout (POST) { card_number, ... } → backend:
   a. Crea orden desde carrito
   b. Procesa pago (mock)
   c. Actualiza estado: "paid" | "failed" | "pending"
   d. Limpia carrito si exitoso
   e. Devuelve { order, payment }
6. Usuario → /orders (GET) → ve historial de pedidos
```

---

## Seguridad (simulada)

- **JWT**: generado con `PyJWT`, firmado con clave secreta
- **Auth interceptor** (Angular): adjunta `Authorization: Bearer <token>` automáticamente
- **Auth guard**: protege rutas `/cart`, `/checkout`, `/orders`
- **Middleware FastAPI**: valida token en endpoints protegidos
- **Contraseñas**: hasheadas con SHA-256 (usar bcrypt en producción)

---

## Stack tecnológico

| Capa        | Tecnología                              |
|-------------|------------------------------------------|
| Frontend    | Angular 18, Angular Material, Signals   |
| Backend     | Python 3.12, FastAPI, Pydantic v2       |
| Auth        | JWT (PyJWT)                             |
| Datos       | JSON files (sin DB real)                |
| Pagos       | Mock service (sin API real)             |
| Estilos     | Angular Material (tema indigo-pink)     |
| Docker      | Dockerfile × 2 + docker-compose        |
